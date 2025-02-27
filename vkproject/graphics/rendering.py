from vkproject.graphics.vulkan import *
from vkproject.math import Viewport, Rect2D, Vec2


class BufferRenderer:
    def __init__(self, buffer):
        self.buffer = buffer

    def bind_pipeline(self, pipeline):
        vkCmdBindPipeline(self.buffer.handle, VK_PIPELINE_BIND_POINT_GRAPHICS, pipeline.handle)

    def set_viewport(self, viewport: Viewport):
        vk_vp = viewport.vk()
        vkCmdSetViewport(self.buffer.handle, 0, 1, [vk_vp])

    def set_scissor(self, scissor: Rect2D):
        vk_rect = scissor.vk()
        vkCmdSetScissor(self.buffer.handle, 0, 1, [vk_rect])

    def no_scissor(self, swap_chain):
        self.set_scissor(Rect2D(Vec2(0, 0), Vec2.from_vk_extent(swap_chain.extent)))

    def draw(self, vertex_count, instance_count, first_vertex, first_instance):
        vkCmdDraw(self.buffer.handle, vertex_count, instance_count, first_vertex, first_instance)

    def sample_render(self, swap_chain):
        self.set_viewport(Viewport(pos=Vec2(0, 0), size=Vec2.from_vk_extent(swap_chain.extent), min_depth=0.0, max_depth=1.0))
        self.no_scissor(swap_chain)
        self.draw(3, 1, 0, 0)
