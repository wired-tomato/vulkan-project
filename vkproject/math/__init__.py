import numpy as np

from vkproject.graphics.vulkan import VkViewport, VkRect2D, VkOffset2D, VkExtent2D


class Vec2:
    def __init__(self, x, y):
        self._array = np.array([x, y])

    @staticmethod
    def from_vk_extent(extent):
        return Vec2(extent.width, extent.height)

    @property
    def x(self):
        return self._array[0]

    @x.setter
    def x(self, value):
        self._array[0] = value

    @property
    def y(self):
        return self._array[1]

    @y.setter
    def y(self, value):
        self._array[1] = value

    def vk_offset_2d(self):
        return VkOffset2D(
            x=self._array[0],
            y=self._array[1],
        )

    def vk_extent_2d(self):
        return VkExtent2D(
            width=self._array[0],
            height=self._array[1],
        )

class Rect2D:
    def __init__(self, pos: Vec2, size: Vec2):
        self.pos = pos
        self.size = size

    def vk(self):
        return VkRect2D(
            self.pos.vk_offset_2d(),
            self.size.vk_extent_2d(),
        )

class Viewport:
    def __init__(self, pos: Vec2, size: Vec2, min_depth, max_depth):
        self.pos = pos
        self.size = size
        self.min_depth = min_depth
        self.max_depth = max_depth

    def vk(self):
        return VkViewport(
            x=self.pos.x,
            y=self.pos.y,
            width=self.size.x,
            height=self.size.y,
            minDepth=self.min_depth,
            maxDepth=self.max_depth,
        )