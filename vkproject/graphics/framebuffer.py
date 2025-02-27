from vkproject.graphics.vulkan import VkFramebufferCreateInfo, vkCreateFramebuffer, vkDestroyFramebuffer


class FrameBuffers:
    def __init__(self, device, render_pass, swap_chain):
        self.device = device
        self.render_pass = render_pass
        self.swap_chain = swap_chain
        self.handles = []

    def create(self):
        for image_view in self.swap_chain.image_views:
            create_info = VkFramebufferCreateInfo(
                renderPass=self.render_pass.handle,
                attachmentCount=1,
                pAttachments=[image_view],
                width=self.swap_chain.extent.width,
                height=self.swap_chain.extent.height,
                layers=1
            )
            handle = vkCreateFramebuffer(self.device, create_info, None)
            self.handles.append(handle)

    def destroy(self):
        for handle in self.handles:
            vkDestroyFramebuffer(self.device, handle, None)
        self.handles = []