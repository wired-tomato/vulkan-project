from graphics.vulkan import vkGetInstanceProcAddr, VK_ERROR_EXTENSION_NOT_PRESENT


def vkCreateDebugUtilsMessengerEXT(instance, pCreateInfo, pAllocator):
    func = vkGetInstanceProcAddr(instance, 'vkCreateDebugUtilsMessengerEXT')
    if func:
        return func(instance, pCreateInfo, pAllocator)
    else:
        return VK_ERROR_EXTENSION_NOT_PRESENT

def vkDestroyDebugUtilsMessengerEXT(instance, messenger, pAllocator):
    func = vkGetInstanceProcAddr(instance, 'vkDestroyDebugUtilsMessengerEXT')
    if func:
        return func(instance, messenger, pAllocator)
    else:
        return VK_ERROR_EXTENSION_NOT_PRESENT