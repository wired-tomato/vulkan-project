import abc
import enum

import vma.lib

from vkproject.graphics.vulkan import *

SIZE_FLOAT = 4
SIZE_INT32 = 4

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

class BufferObject:
    def __init__(self, allocator, allocation, allocation_info):
        self.handle = None
        self.allocator = allocator
        self.allocation = allocation
        self.allocation_info = allocation_info

    def create(self, usage, mem_usage, initial_size=32000000):
        buffer_info = VkBufferCreateInfo(
            usage=usage,
            size=initial_size,
        )

        alloc_create_info = vma.ffi.new("VmaAllocationCreateInfo *")
        alloc_create_info.usage = mem_usage
        alloc_create_info.flags = vma.lib.VMA_ALLOCATION_CREATE_MAPPED_BIT

        self.handle = vma.ffi.new("VkBuffer *")

        vma.lib.vmaCreateBuffer(self.allocator, buffer_info, alloc_create_info, [self.handle], [self.allocation], self.allocation_info)

    def destroy(self):
        vma.lib.vmaDestroyBuffer(self.allocator, self.handle, self.allocation)

class MeshBuffers:
    def __init__(self, index_buffer, vertex_buffer, vertex_buffer_address):
        self.index_buffer = index_buffer
        self.vertex_buffer = vertex_buffer
        self.vertex_buffer_address = vertex_buffer_address

    @staticmethod
    def allocate(device, command_buffer, allocator, allocation, allocation_info, indices, vertices, vertex_format: VertexFormat):
        vertex_buffer_size = len(vertices) * vertex_format.size()
        index_buffer_size = len(indices) * vma.ffi.sizeof("uint32_t")

        vertex_buffer = BufferObject(allocator, allocation, allocation_info)
        vertex_buffer.create(
            VK_BUFFER_USAGE_STORAGE_BUFFER_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT | vma.lib.VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT,
            vma.lib.VMA_MEMORY_USAGE_GPU_ONLY,
            vertex_buffer_size,
        )

        address_info = VkBufferDeviceAddressInfo(
            buffer = vertex_buffer.handle
        )

        vba = vkGetBufferDeviceAddress(device, address_info)

        index_buffer = BufferObject(allocator, allocation, allocation_info)
        index_buffer.create(
            VK_BUFFER_USAGE_INDEX_BUFFER_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT,
            vma.lib.VMA_MEMORY_USAGE_GPU_ONLY,
            index_buffer_size,
        )

        staging = BufferObject(allocator, allocation, allocation_info)
        staging.create(
            VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
            vma.lib.VMA_MEMORY_USAGE_CPU_ONLY,
            vertex_buffer_size + index_buffer_size,
        )

        data = staging.allocation.GetMappedData()
        vma.ffi.memmove(data, vertices, vertex_buffer_size)
        vma.ffi.memmove(data + vertex_buffer_size, indices, index_buffer_size)

        vertex_copy = VkBufferCopy(
            srcOffset=0,
            dstOffset=0,
            size=vertex_buffer_size,
        )

        index_copy = VkBufferCopy(
            srcOffset=vertex_buffer_size,
            dstOffset=0,
            size=index_buffer_size,
        )

        vkCmdCopyBuffer(command_buffer, staging.handle, vertex_buffer.handle, 1, vertex_copy)
        vkCmdCopyBuffer(command_buffer, staging.handle, index_buffer.handle, 1, index_copy)


        return MeshBuffers(index_buffer, vertex_buffer, vba)
