from vulkan import *
import glfw

from vulkan_extensions.vk_ext import *
from vulkan_extensions.vk_khr import *
from windowing import Window


class VkApp:
    def __init__(self, window: Window):
        # window will be needed later in surface creation
        self.window = window
        self._validation_layers = []
        # SwapChain extension is required
        self._device_extensions = [VK_KHR_SWAPCHAIN_EXTENSION_NAME]
        self._enable_validation = False
        self.instance = None
        self._physical_device = None
        self.device = None
        self.queue_family_indices = QueueFamilyIndices()
        self.surface = None
        self._graphics_queue = None
        self._present_queue = None
        self._swap_chain = None
        self._debug_messenger = None

    def init(self):
        self._create_instance()
        self._setup_debug_messenger()
        self._create_surface()
        self._select_physical_device()
        self._create_logical_device()
        self._swap_chain.create()
        self._swap_chain.create_image_views()

    def _create_instance(self):
        # Vulkan app info - capital V indicates creation of C struct
        # sType specifies structure type, required in all vulkan structs
        app_info = VkApplicationInfo(
            # sType=VK_STRUCTURE_TYPE_APPLICATION_INFO - sType is specified by default in bindings,
            pApplicationName=self.window.name(),
            applicationVersion=VK_MAKE_VERSION(1, 0, 0),
            pEngineName=self.window.name(),
            engineVersion=VK_MAKE_VERSION(1, 0, 0),
            apiVersion=VK_API_VERSION_1_0,
        )

        extensions = self._get_extensions()

        # check that validation layers exist on system
        if self._enable_validation and not self._check_for_layers(self._validation_layers):
            raise RuntimeError("Validation layers not available")

        if self._enable_validation:
            layers = self._validation_layers
            extensions.append(VK_EXT_DEBUG_UTILS_EXTENSION_NAME)
        else:
            layers = []

        # instance create info
        create_info = VkInstanceCreateInfo(
            # sType=VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app_info,
            enabledExtensionCount=len(extensions),
            ppEnabledExtensionNames=extensions,  # pass required extensions, will raise exception if any are not found
            enabledLayerCount=len(layers),  # pass enabled validation layers to instance
            ppEnabledLayerNames=layers,
            flags=0
        )

        self.instance = vkCreateInstance(create_info, None)

    def _setup_debug_messenger(self):
        debug_create_info = VkDebugUtilsMessengerCreateInfoEXT(
            messageSeverity=VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT,
            messageType=VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT,
            pfnUserCallback=VkApp._debug_callback
        )
        self._debug_messenger = vkCreateDebugUtilsMessengerEXT(self.instance, debug_create_info, None)

    @staticmethod
    def _debug_callback(message_severity, message_type, p_callback_data, _):
        message = ffi.string(p_callback_data.pMessage).decode("utf-8")
        print(f"VALIDATION LAYER - {VkApp._type(message_type)}: {VkApp._severity(message_severity)}: {message}")

        return VK_FALSE

    @staticmethod
    def _severity(bit):
        if bit == VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT:
            return "VERBOSE"
        elif bit == VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT:
            return "INFO"
        elif bit == VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT:
            return "WARNING"
        elif bit == VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT:
            return "ERROR"

    @staticmethod
    def _type(bit):
        if bit == VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT:
            return "GENERAL"
        elif bit == VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT:
            return "VALIDATION"
        elif bit == VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT:
            return "PERFORMANCE"

    def _select_physical_device(self):
        #returns list of all physical devices (with vulkan support) on the system
        devices = vkEnumeratePhysicalDevices(self.instance)

        for device in devices:
            is_suitable, queue_family_indices, support_details = self._is_device_suitable(device)
            if is_suitable:
                self._physical_device = device
                self.queue_family_indices = queue_family_indices
                self._swap_chain = SwapChain(support_details, self)
                break

        if not self._physical_device:
            raise RuntimeError("No suitable vulkan devices found")

    def _get_queue_info(self):
        queue_info = []
        for idx in self.queue_family_indices.unique_indices():
            queue_create_info = VkDeviceQueueCreateInfo(
                queueFamilyIndex=idx,
                queueCount=1,
                pQueuePriorities=[1.0]
            )
            queue_info.append(queue_create_info)
        return queue_info

    def _create_logical_device(self):
        device_features = VkPhysicalDeviceFeatures()

        if self._enable_validation:
            layers = self._validation_layers
        else:
            layers = []

        device_create_info = VkDeviceCreateInfo(
            pQueueCreateInfos=self._get_queue_info(),
            pEnabledFeatures=[device_features],
            ppEnabledLayerNames=layers,
            ppEnabledExtensionNames=self._device_extensions,
            flags=0
        )

        self.device = vkCreateDevice(self._physical_device, device_create_info, None) # VkDevice*
        self._graphics_queue = vkGetDeviceQueue(self.device, self.queue_family_indices.graphics_family, 0)
        self._present_queue = vkGetDeviceQueue(self.device, self.queue_family_indices.present_family, 0)

    def _create_surface(self):
        # allocate surface ptr to mem using vulkan's FFI obj
        # the size of VkSurfaceKHR_T is unknown by cffi so we cannot allocate it like normal
        # ex: VKSurfaceKHR surface;
        surface_ptr = ffi.new("VkSurfaceKHR*")
        #FFI#addressof returns ptr to c data
        glfw.create_window_surface(self.instance, self.window.handle(), None, surface_ptr)
        # deref the ptr
        self.surface = surface_ptr[0]

    def _find_queue_families(self, device):
        queue_families = vkGetPhysicalDeviceQueueFamilyProperties(device)
        queue_family_indices = QueueFamilyIndices()

        idx = 0
        for queue_family in queue_families:
            if queue_family.queueFlags & VK_QUEUE_GRAPHICS_BIT != 0:
                queue_family_indices.graphics_family = idx

            if vkGetPhysicalDeviceSurfaceSupportKHR(self.instance, device, idx, self.surface) > VK_FALSE:
                queue_family_indices.present_family = idx

            idx += 1

        return queue_family_indices

    def _query_swap_chain_support_details(self, device):
        details = SwapChainSupportDetails()
        details.capabilities = vkGetPhysicalDeviceSurfaceCapabilitiesKHR(self.instance, device, self.surface)
        details.formats = vkGetPhysicalDeviceSurfaceFormatsKHR(self.instance, device, self.surface)
        details.presentModes = vkGetPhysicalDeviceSurfacePresentModesKHR(self.instance, device, self.surface)

        return details

    def _is_device_suitable(self, device):
        #find required indices
        queue_family_indices = self._find_queue_families(device)
        supports_extensions = self._check_device_extension_support(device)

        adequate_swap_chain = False
        swap_chain_support_details = None
        if supports_extensions:
            swap_chain_support_details = self._query_swap_chain_support_details(device)
            adequate_swap_chain = len(swap_chain_support_details.formats) > 0 and len(swap_chain_support_details.presentModes) > 0


        #return queue family indices and swap chain support details so that they don't have to be requeried later
        return (queue_family_indices.is_complete() and supports_extensions and adequate_swap_chain), queue_family_indices, swap_chain_support_details

    def _check_device_extension_support(self, device):
        supported_extensions = vkEnumerateDeviceExtensionProperties(device, None)
        extensions = set(self._device_extensions)

        for supported_extension in supported_extensions:
            ext_name = supported_extension.extensionName
            if ext_name in extensions:
                extensions.remove(ext_name)

        return len(extensions) == 0

    # separate extensions as they will be needed on the device later
    def _get_extensions(self):
        # find platform specific surface extensions - glfw does this for us
        extensions = glfw.get_required_instance_extensions()
        if self._enable_validation:
            extensions.append(VK_EXT_DEBUG_UTILS_EXTENSION_NAME)

        return extensions

    @staticmethod
    def _check_for_layers(layers):
        # get available system layers
        available_layers = list(vkEnumerateInstanceLayerProperties())

        # loop over layers making sure all the requested layers are present on system
        for layer in layers:
            layer_found = False
            for available_layer in available_layers:
                if available_layer.layerName == layer:
                    layer_found = True
                    break

            if not layer_found:
                return False

        return True

    def validation_layer(self, layer):
        self._validation_layers.append(layer)

    def default_validation_layers(self):
        self._validation_layers.append("VK_LAYER_KHRONOS_validation")

    def enable_validation(self):
        self._enable_validation = True

    def disable_validation(self):
        self._enable_validation = False

    def device_extension(self, extension):
        self._device_extensions.append(extension)

    def cleanup(self):
        if self._enable_validation:
            vkDestroyDebugUtilsMessengerEXT(self.instance, self._debug_messenger, None)

        self._swap_chain.cleanup()
        vkDestroyDevice(self.device, None)
        vkDestroySurfaceKHR(self.instance, self.surface, None)
        vkDestroyInstance(self.instance, None)

class SwapChain:
    def __init__(self, support_details, app: VkApp):
        self._support_details = support_details
        self._app = app
        self.surface_format = None
        self.present_mode = None
        self.extent = None
        self._handle = None
        self._images = None
        self._image_views = []

    def create(self):
        self.surface_format = SwapChain._choose_surface_format(self._support_details.formats)
        self.present_mode = SwapChain._choose_present_mode(self._support_details.presentModes)
        self.extent = SwapChain._choose_extent(self._support_details.capabilities, self._app.window)
        # requesting the minimum usually leaves you waiting on the driver for more images to render to
        image_count = self._support_details.capabilities.minImageCount + 1
        if 0 < self._support_details.capabilities.maxImageCount < image_count:
            image_count = self._support_details.capabilities.maxImageCount

        if self._app.queue_family_indices.graphics_family != self._app.queue_family_indices.present_family:
            image_sharing_mode = VK_SHARING_MODE_CONCURRENT
            queue_family_indices = self._app.queue_family_indices.indices()
        else:
            image_sharing_mode = VK_SHARING_MODE_EXCLUSIVE
            queue_family_indices = None

        create_info = VkSwapchainCreateInfoKHR(
            surface=self._app.surface,
            minImageCount=image_count,
            imageFormat=self.surface_format.format,
            imageColorSpace=self.surface_format.colorSpace,
            imageExtent=self.extent,
            imageArrayLayers=1,
            imageUsage=VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
            imageSharingMode=image_sharing_mode,
            pQueueFamilyIndices=queue_family_indices,
            preTransform=self._support_details.capabilities.currentTransform,
            compositeAlpha=VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
            presentMode=self.present_mode,
            clipped=VK_TRUE,
            oldSwapchain=self._handle
        )

        self._handle = vkCreateSwapchainKHR(self._app.device, create_info, None)
        self._images = vkGetSwapchainImagesKHR(self._app.device, self._handle)

    def create_image_views(self):
        for image in self._images:
            image_view_create_info = VkImageViewCreateInfo(
                image=image,
                viewType=VK_IMAGE_VIEW_TYPE_2D,
                format=self.surface_format.format,
                components=VkComponentMapping(VK_COMPONENT_SWIZZLE_IDENTITY, VK_COMPONENT_SWIZZLE_IDENTITY, VK_COMPONENT_SWIZZLE_IDENTITY, VK_COMPONENT_SWIZZLE_IDENTITY),
                subresourceRange=VkImageSubresourceRange(
                    aspectMask=VK_IMAGE_ASPECT_COLOR_BIT,
                    baseMipLevel=0,
                    levelCount=1,
                    baseArrayLayer=0,
                    layerCount=1,
                ),
            )

            image_view = vkCreateImageView(self._app.device, image_view_create_info, None)
            self._image_views.append(image_view)

    def cleanup(self):
        for view in self._image_views:
            vkDestroyImageView(self._app.device, view, None)

        vkDestroySwapchainKHR(self._app.device, self._handle, None)

    @staticmethod
    def _choose_surface_format(available_formats):
        for surface_format in available_formats:
            if (surface_format.format == VK_FORMAT_B8G8R8A8_SRGB) and (surface_format.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR):
                return surface_format

        return available_formats[0]

    @staticmethod
    def _choose_present_mode(available_present_modes):
        for present_mode in available_present_modes:
            if present_mode == VK_PRESENT_MODE_MAILBOX_KHR:
                return present_mode

        #Gaurenteed to be present
        return VK_PRESENT_MODE_FIFO_KHR

    @staticmethod
    def _choose_extent(capabilities, window):
        if capabilities.currentExtent.width != 2**32:
            return capabilities.currentExtent
        else:
            width, height = glfw.get_framebuffer_size(window.handle())
            extent = VkExtent2D(
                max(min(width, capabilities.maxImageExtent.width), capabilities.minImageExtent.width),
                max(min(height, capabilities.maxImageExtent.height), capabilities.minImageExtent.height)
            )
            return extent

class QueueFamilyIndices:
    def __init__(self, graphics_family=None, present_family=None):
        self.graphics_family = graphics_family
        self.present_family = present_family

    def indices(self):
        return [ self.graphics_family, self.present_family ]

    def unique_indices(self):
        return set(self.indices())

    def is_complete(self) -> bool:
        return self.graphics_family is not None and self.present_family is not None

class SwapChainSupportDetails:
    def __init__(self):
        self.capabilities = None
        self.formats = None
        self.presentModes = None
