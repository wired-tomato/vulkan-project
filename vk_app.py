from vulkan import *
import glfw

from vk_ext import vkCreateDebugReportCallbackEXT
from windowing import Window


class VkApp:
    def __init__(self, window: Window):
        # window will be needed later in surface creation
        self._window = window
        self._validation_layers = []
        self._enable_validation = False
        self._instance = None
        self._debug_callback = None

    def create_instance(self):
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

    def setup_debug_messenger(self):
        debugCreateInfo = VkDebugUtilsMessengerCreateInfoEXT(
            messageSeverity=VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT,
            messageType=VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT,
            pfnUserCallback=self.__debugCallback
        )
        self._debug_callback = vkCreateDebugReportCallbackEXT(self._instance, debugCreateInfo, None)

    def __debugCallback(*args):
        print('DEBUG: {} {}'.format(args[5], args[6]))
        return VK_FALSE

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
