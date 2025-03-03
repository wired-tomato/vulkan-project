import abc
import enum

from vkproject.graphics.vulkan import VkVertexInputBindingDescription, VK_VERTEX_INPUT_RATE_VERTEX, \
    VkVertexInputAttributeDescription, VK_FORMAT_R32_SFLOAT, VK_FORMAT_R32G32_SFLOAT, VK_FORMAT_R32G32B32_SFLOAT, \
    VK_FORMAT_R32G32B32A32_SFLOAT, VkBufferCreateInfo

SIZE_FLOAT = 4

class VertexFormat(abc.ABC):
    @abc.abstractmethod
    def binding_description(self):
        pass

    def _binding_description(self, rate):
        return VkVertexInputBindingDescription(
            binding=self.id(),
            stride=self.size(),
            inputRate=rate
        )

    @abc.abstractmethod
    def attribute_descriptions(self):
        pass

    def _attr(self, location, v_format, offset):
        return VkVertexInputAttributeDescription(
            location=location,
            binding=self.id(),
            format=v_format,
            offset=offset
        )

    def _float_attr(self, location, offset):
        return self._attr(location, VK_FORMAT_R32_SFLOAT, offset)

    def _vec2f_attr(self, location, offset):
        return self._attr(location, VK_FORMAT_R32G32_SFLOAT, offset)

    def _vec3f_attr(self, location, offset):
        return self._attr(location, VK_FORMAT_R32G32B32_SFLOAT, offset)

    def _vec4f_attr(self, location, offset):
        return self._attr(location, VK_FORMAT_R32G32B32A32_SFLOAT, offset)

    @abc.abstractmethod
    def id(self):
        pass
    @abc.abstractmethod
    def size(self) -> int:
        pass

#A vertex format describing 2 3d vectors, pos -> color
class PosColor(VertexFormat):
    def binding_description(self):
        return self._binding_description(VK_VERTEX_INPUT_RATE_VERTEX)

    def attribute_descriptions(self):
        return [
            self._vec3f_attr(0, 0),
            #C++ usually has offsetof(Struct, member) but we don't get those luxuries, it's okay because I know color will be 3 floats after pos
            self._vec3f_attr(1, SIZE_FLOAT*3),
        ]

    def id(self):
        return 0

    def size(self) -> int:
        #never thought I'd miss sizeof(Struct) in python but here we are
        return SIZE_FLOAT * 6

class VertexFormats(enum.Enum):
    POS_COLOR = PosColor()

class VertexBuffer:
    def __init__(self):
        self.handle = None

    def create(self, usage, sharing_mode, initial_size=32000000):
        buffer_info = VkBufferCreateInfo()
