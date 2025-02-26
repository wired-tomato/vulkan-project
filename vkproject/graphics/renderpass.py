from vkproject.graphics.vulkan import *


class RenderPass:
    def __init__(self, app):
        self._app = app
        self.handle = None

    def create(self):
        color_attachment = VkAttachmentDescription(
            format=self._app.swap_chain.surface_format.format,
            samples=VK_SAMPLE_COUNT_1_BIT,
            loadOp=VK_ATTACHMENT_LOAD_OP_CLEAR, # clear existing values in attachment
            storeOp=VK_ATTACHMENT_STORE_OP_STORE, # rendered contents will be stored in memory and can be read later
            stencilLoadOp=VK_ATTACHMENT_LOAD_OP_DONT_CARE,
            stencilStoreOp=VK_ATTACHMENT_STORE_OP_DONT_CARE,
            initialLayout=VK_IMAGE_LAYOUT_UNDEFINED,
            finalLayout=VK_IMAGE_LAYOUT_PRESENT_SRC_KHR, # presentable to swap chain
        )

        color_attachment_ref = VkAttachmentReference(
            attachment=0,
            layout=VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL
        )

        subpass = VkSubpassDescription(
            pipelineBindPoint=VK_PIPELINE_BIND_POINT_GRAPHICS,
            colorAttachmentCount=1,
            pColorAttachments=[color_attachment_ref],
        )

        create_info = VkRenderPassCreateInfo(
            attachmentCount=1,
            pAttachments=[color_attachment],
            subpassCount=1,
            pSubpasses=[subpass],
        )

        self.handle = vkCreateRenderPass(self._app.device, create_info, None)

    def begin(self, command_buffer, frame_buffers, image_idx):
        clear_color = VkClearColorValue(float32=[0.0, 0.0, 0.0, 1.0])
        info = VkRenderPassBeginInfo(
            renderPass=self.handle,
            framebuffer=frame_buffers.handles[image_idx],
            renderArea=VkRect2D(
                offset=VkOffset2D(0.0, 0.0),
                extent=self._app.swap_chain.extent
            ),
            pClearValues=[clear_color],
        )

        vkCmdBeginRenderPass(command_buffer.handle, info, VK_SUBPASS_CONTENTS_INLINE)

    def end(self, command_buffer):
        vkCmdEndRenderPass(command_buffer.handle)

    def destroy(self):
        vkDestroyRenderPass(self._app.device, self.handle, None)