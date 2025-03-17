import re
from pathlib import Path

from cffi import FFI

ROOT = Path(__file__).parent

ffibuilder = FFI()

with open(Path(ROOT, "vma.cdef.h")) as psrc:
    data: str = psrc.read()

data = re.sub(r"_Nonnull", "", data)
data = re.sub(r"_Nullable", "", data)

first_valid_statement = data.index("typedef uint32_t VkBool32;")
data = data[first_valid_statement:]

ffibuilder.cdef(data)

include_dirs = [Path(ROOT, "../../include").absolute()]
include_args = [f"-I{x}" for x in include_dirs]

libs = ["volk"]

with open(Path(ROOT, "../../include/vk_mem_alloc.h")) as source_file:
    source_data = source_file.read()

source_data = "#define VK_NO_PROTOTYPES 1\n" + source_data

ffibuilder.set_source(
    "vma",
    """
    #define VMA_IMPLEMENTATION
    #include "vk_mem_alloc.h"
    """,
    libraries=libs,
    library_dirs=[str(ROOT.absolute()), "C:\\VulkanSDK\\1.4.304.1\\Lib"],
    source_extension=".cpp",
    extra_compile_args=include_args,
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
