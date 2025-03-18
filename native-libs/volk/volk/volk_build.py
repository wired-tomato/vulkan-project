import os
import re
import sys
from pathlib import Path

from cffi import FFI

ROOT = Path(__file__).parent

ffibuilder = FFI()

with open(Path(ROOT, "volk.cdef.h")) as psrc:
    data: str = psrc.read()

data = re.sub(r"_Nonnull", "", data)
data = re.sub(r"_Nullable", "", data)

first_valid_statement = data.index("typedef uint32_t VkBool32;")
data = data[first_valid_statement:]

ffibuilder.cdef(data)

include_dirs = [Path(ROOT, "../../include").absolute()]
include_args = [f"-I{x}" for x in include_dirs]

libs = []

platform = None
if sys.platform == "win32":
    platform = "WIN32_KHR"
elif sys.platform == "linux" or sys.platform == "linux2":
    session_type = os.environ["XDG_SESSION_TYPE"]
    if session_type == "wayland":
        platform = "WAYLAND_KHR"
    else:
        platform = "XLIB_KHR"
elif sys.platform == "darwin":
    platform = "MACOS_MKV"

ffibuilder.set_source(
    "volk",
    f"""
    #define VK_USE_PLATFORM_{platform}
    #define VOLK_IMPLEMENTATION
    #include "Volk/volk.h"
    """,
    libraries=libs,
    library_dirs=[str(ROOT.absolute()), "C:\\VulkanSDK\\1.4.304.1\\Lib"],
    source_extension=".cpp",
    extra_compile_args=include_args,
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
