from vulkan import vkGetInstanceProcAddr, VK_ERROR_EXTENSION_NOT_PRESENT, ffi


def vkCreateDebugUtilsMessengerEXT(instance, pCreateInfo, pAllocator):
    func = vkGetInstanceProcAddr(instance, 'vkCreateDebugUtilsMessengerEXT')
    if func:
        return func(instance, pCreateInfo, pAllocator)
    else:
        return VK_ERROR_EXTENSION_NOT_PRESENT