from vkproject.graphics.commands import CommandPool, CommandBuffer
from vkproject.graphics.framebuffer import FrameBuffers
from vkproject.graphics.pipeline import GraphicsPipeline
from vkproject.graphics.rendering import BufferRenderer
from vkproject.graphics.renderpass import RenderPass
import glfw

from vkproject.graphics.swapchain import SwapChain, SwapChainSupportDetails
from vkproject.graphics.vulkan import *
from vkproject.graphics.vulkan.extensions.ext import *
from vkproject.graphics.vulkan.extensions.khr import *
from vkproject.resources import Resources
from vkproject.resources.shaders import ShaderType, ShaderLoader
from vkproject.windowing import Window


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
        self.swap_chain = None
        self.render_pass = RenderPass(self)
        self._shaders = Resources.get_loader(ShaderLoader)
        self.pipeline = GraphicsPipeline(self, { ShaderType.VERTEX: self._shaders.default_vertex, ShaderType.FRAGMENT: self._shaders.default_frag })
        self.frame_buffers = FrameBuffers(self)
        self.command_pool = None
        self.command_buffer = None
        self._debug_messenger = None

    def init(self):
        self._create_instance()
        self._setup_debug_messenger()
        self._create_surface()
        self._select_physical_device()
        self._create_logical_device()
        self.command_pool = CommandPool(self.device, self.queue_family_indices.graphics_family)
        self.swap_chain.create()
        self.swap_chain.create_image_views()
        self.render_pass.create()
        self.frame_buffers.create()
        self.pipeline.create()
        self.command_pool.create()
        self.command_buffer = CommandBuffer(self.device, self.command_pool)
        self.command_buffer.create()

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
        else:
            return None

    @staticmethod
    def _type(bit):
        if bit == VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT:
            return "GENERAL"
        elif bit == VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT:
            return "VALIDATION"
        elif bit == VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT:
            return "PERFORMANCE"
        else:
            return None

    def _select_physical_device(self):
        #returns list of all physical devices (with vulkan support) on the system
        devices = vkEnumeratePhysicalDevices(self.instance)

        for device in devices:
            is_suitable, queue_family_indices, support_details = self._is_device_suitable(device)
            if is_suitable:
                self._physical_device = device
                self.queue_family_indices = queue_family_indices
                self.swap_chain = SwapChain(support_details, self)
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

    def record_command_buffer(self, image_idx):
        self.command_buffer.begin_recording()
        self.render_pass.begin(self.command_buffer, self.frame_buffers, image_idx)
        renderer = BufferRenderer(self.command_buffer)
        renderer.bind_pipeline(self.pipeline)
        renderer.sample_render(self.swap_chain)
        self.render_pass.end(self.command_buffer)
        self.command_buffer.end_recording()

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
        self.command_pool.destroy()
        self.pipeline.destroy()
        self.frame_buffers.destroy()
        self.render_pass.destroy()
        self.swap_chain.destroy()
        vkDestroyDevice(self.device, None)
        vkDestroySurfaceKHR(self.instance, self.surface, None)

        if self._enable_validation:
            vkDestroyDebugUtilsMessengerEXT(self.instance, self._debug_messenger, None)

        vkDestroyInstance(self.instance, None)

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
