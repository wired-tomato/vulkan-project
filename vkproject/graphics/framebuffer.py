from vkproject.graphics.vulkan import VkFramebufferCreateInfo, vkCreateFramebuffer, vkDestroyFramebuffer


class FrameBuffers:
    def __init__(self, app):
        self._app = app
        self.handles = []

    def create(self):
        for image_view in self._app.swap_chain.image_views:
            create_info = VkFramebufferCreateInfo(
                renderPass=self._app.render_pass.handle,
                attachmentCount=1,
                pAttachments=[image_view],
                width=self._app.swap_chain.extent.width,
                height=self._app.swap_chain.extent.height,
                layers=1
            )
            handle = vkCreateFramebuffer(self._app.device, create_info, None)
            self.handles.append(handle)

    def destroy(self):
        for handle in self.handles:
            vkDestroyFramebuffer(self._app.device, handle, None)