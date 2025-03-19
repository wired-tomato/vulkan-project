import vma


class VmaAllocator:
    def __init__(self):
        self.handle = None

    def init(self, vk_fn_table, physical_device, device, instance):
        vma_vk_functions = vma.ffi.new("VmaVulkanFunctions *")
        for name, fn in vk_fn_table.items():
            setattr(vma_vk_functions, name, fn)

        create_info = vma.ffi.new("VmaAllocatorCreateInfo *")
        create_info.physicalDevice = physical_device
        create_info.device = device
        create_info.instance = instance
        create_info.flags = vma.lib.VMA_ALLOCATOR_CREATE_BUFFER_DEVICE_ADDRESS_BIT
        create_info.pVulkanFunctions = vma_vk_functions

        self.handle = vma.ffi.new("VmaAllocator *")
        vma.lib.vmaCreateAllocator(create_info, self.handle)
