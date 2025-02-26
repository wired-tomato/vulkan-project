import enum

from vkproject.graphics.vulkan import *


class CommandPool:
    def __init__(self, device, queue_family):
        self._device = device
        self._queue_family = queue_family
        self.handle = None
        self._transient = False

    def transient(self):
        self._transient = True

    def rcb(self):
        self._transient = False

    def create(self):
        if self._transient:
            flags = VK_COMMAND_POOL_CREATE_TRANSIENT_BIT
        else:
            flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT

        create_info = VkCommandPoolCreateInfo(
            flags=flags,
            queueFamilyIndex=self._queue_family,
        )

        self.handle = vkCreateCommandPool(self._device, create_info, None)

    def destroy(self):
        vkDestroyCommandPool(self._device, self.handle, None)

class CommandBufferRecordingType(enum.Enum):
    NONE = 0
    ONE_TIME_SUBMIT = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT
    RENDER_PASS_CONTINUE = VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT,
    SIMULTANEOUS = VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT

class CommandBuffer:
    def __init__(self, device, pool):
        self._device = device
        self._pool = pool
        self._primary = True
        self.handle = None

    def primary(self):
        self._primary = True

    def secondary(self):
        self._primary = False

    def create(self):
        if self._primary:
            level = VK_COMMAND_BUFFER_LEVEL_PRIMARY
        else:
            level = VK_COMMAND_BUFFER_LEVEL_SECONDARY

        alloc_info = VkCommandBufferAllocateInfo(
            commandPool=self._pool.handle,
            level=level,
            commandBufferCount=1,
        )

        self.handle = vkAllocateCommandBuffers(self._device, alloc_info)

    def begin_recording(self, recording_type = CommandBufferRecordingType.NONE):
        begin_info = VkCommandBufferBeginInfo(flags=recording_type.value, pInheritanceInfo=None)
        vkBeginCommandBuffer(self.handle, begin_info)

    def end_recording(self):
        vkEndCommandBuffer(self.handle)