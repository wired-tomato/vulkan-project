from vulkan import *
import glfw

from vk_ext import vkCreateDebugUtilsMessengerEXT
from windowing import Window


class VkApp:
    def __init__(self, window: Window):
        # window will be needed later in surface creation
        self._window = window
        self._validation_layers = []
        self._enable_validation = False
        self._instance = None
        self._debug_callback = None
        self._physical_device = None
        self._queue_family_indices = QueueFamilyIndices(None)

    def init(self):
        self._create_instance()
        self._setup_debug_messenger()
        self._select_physical_device()

    def _create_instance(self):
        # Vulkan app info - capital V indicates creation of C struct
        # sType specifies structure type, required in all vulkan structs
        app_info = VkApplicationInfo(
            # sType=VK_STRUCTURE_TYPE_APPLICATION_INFO - sType is specified by default in bindings,
            pApplicationName=self._window.name(),
            applicationVersion=VK_MAKE_VERSION(1, 0, 0),
            pEngineName=self._window.name(),
            engineVersion=VK_MAKE_VERSION(1, 0, 0),
            apiVersion=VK_API_VERSION_1_0,
        )

        extensions = self.get_extensions()

        # check that validation layers exist on system
        if self._enable_validation and not self.check_for_layers(self._validation_layers):
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

        self._instance = vkCreateInstance(create_info, None)

    def _setup_debug_messenger(self):
        debug_create_info = VkDebugUtilsMessengerCreateInfoEXT(
            messageSeverity=VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT,
            messageType=VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT,
            pfnUserCallback=self.__debugCallback
        )
        self._debug_callback = vkCreateDebugUtilsMessengerEXT(self._instance, debug_create_info, None)

    def __debugCallback(*args):
        print("VULKAN DEBUG: {} {}".format(args[1], args[2]))
        return VK_FALSE

    def _select_physical_device(self):
        #returns list of all physical devices (with vulkan support) on the system
        devices = vkEnumeratePhysicalDevices(self._instance)

        for device in devices:
            is_suitable, queue_family_indices = self.is_device_suitable(device)
            if is_suitable:
                self._physical_device = device
                self._queue_family_indices = queue_family_indices
                break

        if not self._physical_device:
            raise RuntimeError("No suitable vulkan devices found")

    def find_queue_families(self, device):
        queue_families = vkGetPhysicalDeviceQueueFamilyProperties(device)
        queue_family_indices = QueueFamilyIndices()

        idx = 0
        for queue_family in queue_families:
            if queue_family.queueFlags & VK_QUEUE_GRAPHICS_BIT != 0:
                queue_family_indices.graphics_family = idx

            idx += 1

        return queue_family_indices

    def is_device_suitable(self, device):
        #find required indices
        queue_family_indices = self.find_queue_families(device)

        #return if the queues are complete and the queues to avoid queue searching twice
        return queue_family_indices.is_complete(), queue_family_indices

    # seperate extensions as they will be needed on the device later
    def get_extensions(self):
        # find platform specific surface extensions - glfw does this for us
        extensions = glfw.get_required_instance_extensions()
        if self._enable_validation:
            extensions.append(VK_EXT_DEBUG_UTILS_EXTENSION_NAME)

        return extensions

    def check_for_layers(self, layers):
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

    def validation_layer(self, name):
        self._validation_layers.append(name)

    def enable_validation(self):
        self._enable_validation = True

    def disable_validation(self):
        self._enable_validation = False

    def cleanup(self):
        vkDestroyInstance(self._instance, None)

class QueueFamilyIndices:
    def __init__(self, graphics_family=None):
        self.graphics_family = graphics_family

    def is_complete(self) -> bool:
        return self.graphics_family is not None
