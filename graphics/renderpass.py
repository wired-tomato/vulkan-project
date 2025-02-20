from graphics.vulkan import *


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

    def cleanup(self):
        vkDestroyRenderPass(self._app.device, self.handle, None)