import glfw

from vkproject.graphics.framebuffer import FrameBuffers
from vkproject.graphics.synchronization import SyncHandler
from vkproject.graphics.vulkan import *
from vkproject.graphics.vulkan.extensions.khr import *


class SwapChainSupportDetails:
    def __init__(self):
        self.capabilities = None
        self.formats = None
        self.presentModes = None

class SwapChain:
    def __init__(self, support_details: SwapChainSupportDetails, window, surface, queue_family_indices, device, command_pool, render_pass, max_frames_in_flight):
        self._support_details = support_details
        self.window = window
        self.surface = surface
        self.queue_family_indices = queue_family_indices
        self.device = device
        self.command_pool = command_pool
        self.render_pass = render_pass

        self.surface_format = None
        self.present_mode = None
        self.extent = None
        self.handle = None
        self._images = None
        self.image_views = []
        self.frames_in_flight = max_frames_in_flight
        self.command_buffers = []
        self.sync_handlers = [SyncHandler(device) for _ in range(max_frames_in_flight)]

    def create(self):
        self.surface_format = SwapChain._choose_surface_format(self._support_details.formats)
        self.present_mode = SwapChain._choose_present_mode(self._support_details.presentModes)
        self.extent = SwapChain._choose_extent(self._support_details.capabilities, self.window)
        # requesting the minimum usually leaves you waiting on the driver for more images to render to
        image_count = self._support_details.capabilities.minImageCount + 1
        if 0 < self._support_details.capabilities.maxImageCount < image_count:
            image_count = self._support_details.capabilities.maxImageCount

        if self.queue_family_indices.graphics_family != self.queue_family_indices.present_family:
            image_sharing_mode = VK_SHARING_MODE_CONCURRENT
            queue_family_indices = list(self.queue_family_indices.unique_indices())
        else:
            image_sharing_mode = VK_SHARING_MODE_EXCLUSIVE
            queue_family_indices = None

        create_info = VkSwapchainCreateInfoKHR(
            surface=self.surface,
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
            oldSwapchain=VK_NULL_HANDLE
        )

        self.handle = vkCreateSwapchainKHR(self.device, create_info, None)
        self._images = vkGetSwapchainImagesKHR(self.device, self.handle)

        self.command_buffers = self.command_pool.create_command_buffers(self.frames_in_flight)
        for sync_handler in self.sync_handlers:
            sync_handler.create()

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

            image_view = vkCreateImageView(self.device, image_view_create_info, None)
            self.image_views.append(image_view)

    def recreate(self, frame_buffers):
        SyncHandler.wait_idle(self.device)
        self.destroy()
        frame_buffers.destroy()
        self.create()
        self.create_image_views()
        frame_buffers.create()

    def acquire(self, frame, frame_buffers):
        try:
            return vkAcquireNextImageKHR(self.device, self.handle, UINT64_MAX, self.sync_handlers[frame].image_available_semaphore, VK_NULL_HANDLE)
        except (VkErrorOutOfDateKhr, VkSuboptimalKhr) as _:
            self.recreate(frame_buffers)
            return None

    def get_buffer(self, frame):
        return self.command_buffers[frame]

    def get_sync_handler(self, frame):
        return self.sync_handlers[frame]

    def destroy(self):
        for sync_handler in self.sync_handlers:
            sync_handler.destroy()

        for view in self.image_views:
            vkDestroyImageView(self.device, view, None)

        self.image_views = []

        vkDestroySwapchainKHR(self.device, self.handle, None)

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