from vulkan import *

from resources.shaders import Shader, ShaderType
from vk_app import VkApp


class GraphicsPipeline:
    def __init__(self, app: VkApp, shaders: dict[ShaderType, Shader]):
        self._app = app
        self._shaders = shaders
        self._handle = None

    def init(self):
        modules = []
        stages = []

        for shader_type, shader in self._shaders.items():
            module = self._create_shader_module(shader)
            stage_info = VkPipelineShaderStageCreateInfo(
                stage = shader_type.stage(),
                module=module,
                pName="main" # entrypoint name
            )
            modules.append(module)
            stages.append(stage_info)

        for module in modules:
            vkDestroyShaderModule(self._app, module, None)

    def _create_shader_module(self, shader: Shader):
        create_info = VkShaderModuleCreateInfo(
            codeSize = len(shader.data),
            pCode = shader.data
        )

        return vkCreateShaderModule(self._app.device, create_info, None)
