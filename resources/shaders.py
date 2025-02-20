import enum
from pathlib import Path

from graphics.vulkan import VK_SHADER_STAGE_VERTEX_BIT, VK_SHADER_STAGE_FRAGMENT_BIT

from resources import ResourceLoader


class ShaderType(enum.Enum):
    VERTEX = "vert"
    FRAGMENT = "frag"

    def stage(self):
        if self == ShaderType.VERTEX:
            return VK_SHADER_STAGE_VERTEX_BIT
        elif self == ShaderType.FRAGMENT:
            return VK_SHADER_STAGE_FRAGMENT_BIT

class Shader:
    def __init__(self, shader_type: ShaderType, data: bytes):
        self.type: ShaderType = shader_type
        self.data: bytes = data

class ShaderLoader(ResourceLoader):
    def __init__(self):
        self.shaders: dict[ShaderType, dict[str, Shader]] = dict()
        self.default_vertex = None
        self.default_frag = None

    def load_resource(self, resource_path, resource_id):
        shader_type = ShaderType(resource_id.split(".")[-1])
        self.shaders.setdefault(shader_type, dict())
        with open(resource_path, "rb") as shader:
            shader_data = shader.read()

        shader_id = Path(resource_id).stem
        shader = Shader(shader_type, shader_data)
        self.shaders[shader_type][shader_id] = shader

        if shader_id == "default":
            if shader_type == ShaderType.VERTEX:
                self.default_vertex = shader
            elif shader_type == ShaderType.FRAGMENT:
                self.default_frag = shader

    def accepts_resource(self, resource_path, resource_id) -> bool:
        return resource_path.endswith(".spv")
