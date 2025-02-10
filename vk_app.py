import vulkan as vk
import glfw

from windowing import Window


class VkApp:
    def __init__(self, window: Window):
        # window will be needed later in surface creation
        self._window = window
        self._validation_layers = []
        self._enable_validation = False
        self._instance = None

    def create_instance(self):
        # Vulkan app info - capital V indicates creation of C struct
        # sType specifies structure type, required in all vulkan structs
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName=self._window.name(),
            applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            pEngineName=self._window.name(),
            engineVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            apiVersion=vk.VK_API_VERSION_1_0,
        )

        # find platform specific surface extensions - glfw does this for us
        platform_extensions = glfw.get_required_instance_extensions()

        #check that validation layers exist on system
        if self._enable_validation and not self.check_for_layers(self._validation_layers):
            raise RuntimeError("Validation layers not available")

        if self._enable_validation:
            layers = self._validation_layers
        else:
            layers = []

        # instance create info
        create_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app_info,
            enabledExtensionCount=len(platform_extensions),
            ppEnabledExtensionNames=platform_extensions, # pass required extensions, will raise exception if any are not found
            enabledLayerCount=len(layers), # pass enabled validation layers to instance
            ppEnabledLayerNames=layers,
            flags=0
        )

        self._instance = vk.vkCreateInstance(create_info, None)

    def check_for_layers(self, layers):
        # get available system layers
        available_layers = list(vk.vkEnumerateInstanceLayerProperties())

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
        vk.vkDestroyInstance(self._instance, None)

