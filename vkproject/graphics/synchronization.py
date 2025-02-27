from vkproject.graphics.vulkan import *
from vkproject.graphics.vulkan.extensions.khr import vkAcquireNextImageKHR


class SyncHandler:
    def __init__(self, device):
        self.device = device
        self.image_available_semaphore = None
        self.render_finished_semaphore = None
        self.in_flight_fence = None

    def create(self):
        semaphore_info = VkSemaphoreCreateInfo()
        fence_info = VkFenceCreateInfo(
            flags=VK_FENCE_CREATE_SIGNALED_BIT
        )

        self.image_available_semaphore = vkCreateSemaphore(self.device, semaphore_info, None)
        self.render_finished_semaphore = vkCreateSemaphore(self.device, semaphore_info, None)
        self.in_flight_fence = vkCreateFence(self.device, fence_info, None)

    def buffer_submission_info(self, buffer_handles, wait_stages):
        return VkSubmitInfo(
            pWaitSemaphores=[self.image_available_semaphore],
            pWaitDstStageMask=wait_stages,
            pCommandBuffers=buffer_handles,
            pSignalSemaphores=[self.render_finished_semaphore],
        )

    def presentation_info(self, swap_chain_handles, image_idx):
        return VkPresentInfoKHR(
            pWaitSemaphores=[self.render_finished_semaphore],
            pSwapchains=swap_chain_handles,
            pImageIndices=[image_idx],
            pResults=None
        )

    @staticmethod
    def wait_idle(device):
        vkDeviceWaitIdle(device)

    def wait_for_fence(self):
        vkWaitForFences(self.device, 1, [self.in_flight_fence], VK_TRUE, UINT64_MAX)

    def reset_fence(self):
        vkResetFences(self.device, 1, [self.in_flight_fence])

    def destroy(self):
        vkDestroySemaphore(self.device, self.image_available_semaphore, None)
        vkDestroySemaphore(self.device, self.render_finished_semaphore, None)
        vkDestroyFence(self.device, self.in_flight_fence, None)