from vkproject.graphics.vulkan import vkGetInstanceProcAddr, vkGetDeviceProcAddr


def vkDestroySurfaceKHR(instance, surface, allocator):
    func = vkGetInstanceProcAddr(instance, "vkDestroySurfaceKHR")
    return func(instance, surface, allocator)

def vkGetPhysicalDeviceSurfaceSupportKHR(instance, device, queue_family_idx, surface):
    func = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceSupportKHR")
    return func(device, queue_family_idx, surface)

def vkGetPhysicalDeviceSurfaceCapabilitiesKHR(instance, device, surface):
    func = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceCapabilitiesKHR")
    return func(device, surface)

def vkGetPhysicalDeviceSurfaceFormatsKHR(instance, device, surface):
    func = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceFormatsKHR")
    return func(device, surface)

def vkGetPhysicalDeviceSurfacePresentModesKHR(instance, device, surface):
    func = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfacePresentModesKHR")
    return func(device, surface)

def vkCreateSwapchainKHR(device, pCreateInfo, pAllocator):
    func = vkGetDeviceProcAddr(device, "vkCreateSwapchainKHR")
    return func(device, pCreateInfo, pAllocator)

def vkDestroySwapchainKHR(device, swapchain, allocator):
    func = vkGetDeviceProcAddr(device, "vkDestroySwapchainKHR")
    return func(device, swapchain, allocator)

def vkGetSwapchainImagesKHR(device, swapchain):
    func = vkGetDeviceProcAddr(device, "vkGetSwapchainImagesKHR")
    return func(device, swapchain)

def vkAcquireNextImageKHR(device, swapchain, timeout, semaphore, fence):
    func = vkGetDeviceProcAddr(device, "vkAcquireNextImageKHR")
    return func(device, swapchain, timeout, semaphore, fence)

def vkQueuePresentKHR(device, queue, pPresentInfo):
    func = vkGetDeviceProcAddr(device, "vkQueuePresentKHR")
    return func(queue, pPresentInfo)
