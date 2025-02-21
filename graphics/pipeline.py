from graphics.vulkan import *

from resources.shaders import Shader, ShaderType


class GraphicsPipeline:
    def __init__(self, app, shaders: dict[ShaderType, Shader]):
        self._app = app
        self._shaders = shaders
        self._layout = None
        self._handle = None

    def create(self):
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

        #Values that are likely to change so that the graphics pipeline doesn't have to be recreated on render
        dynamic_states = [
            VK_DYNAMIC_STATE_VIEWPORT,
            VK_DYNAMIC_STATE_SCISSOR
        ]

        dynamic_state_info = VkPipelineDynamicStateCreateInfo(
            pDynamicStates=dynamic_states,
        )

        vertex_input_info = VkPipelineVertexInputStateCreateInfo(
            vertexBindingDescriptionCount=0,
            pVertexBindingDescriptions=None,
            vertexAttributeDescriptionCount=0,
            pVertexAttributeDescriptions=None,
        )

        input_assembly_info = VkPipelineInputAssemblyStateCreateInfo(
            topology=VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST, # 3 vertices per triangle with no reuse
            primitiveRestartEnable=VK_FALSE, # when this is true it allows the element buffer to use the special indices 0xFFFF and 0xFFFFFFFF to breakup lines and triangles in STRIP modes
        )

        viewport = VkViewport(
            x=0.0,
            y=0.0,
            width=self._app.swap_chain.extent.width,
            height=self._app.swap_chain.extent.height,
            minDepth=0.0,
            maxDepth=1.0
        )

        scissor = VkRect2D(
            offset=VkOffset2D(0.0, 0.0),
            extent=self._app.swap_chain.extent,
        )

        viewport_state = VkPipelineViewportStateCreateInfo(
            viewportCount=1,
            scissorCount=1,
            pViewports=[viewport],
            pScissors=[scissor],
        )

        rasterizer = VkPipelineRasterizationStateCreateInfo(
            depthClampEnable=VK_FALSE, # enabling this clamps depth values outside the viewport's range instead of discarding them
            rasterizerDiscardEnable=VK_FALSE, # if this is true geometry never passes through rasterization effectively disabling framebuffer output
            polygonMode=VK_POLYGON_MODE_FILL,
            lineWidth=1.0,
            cullMode=VK_CULL_MODE_BACK_BIT,
            depthBiasEnable=VK_FALSE,
            depthBiasConstantFactor=0.0,
            depthBiasClamp=0.0,
            depthBiasSlopeFactor=0.0
        )

        multisampling = VkPipelineMultisampleStateCreateInfo(
            sampleShadingEnable=VK_FALSE,
            rasterizationSamples=VK_SAMPLE_COUNT_1_BIT,
            minSampleShading=1.0,
            pSampleMask=None,
            alphaToCoverageEnable=VK_FALSE,
            alphaToOneEnable=VK_FALSE,
        )

        # Alpha blending roughly equivalent to the following
        # finalColor.rgb = newAlpha * newColor + (1 - newAlpha) * oldColor;
        # finalColor.a = newAlpha.a;
        color_blend_attachment = VkPipelineColorBlendAttachmentState(
            colorWriteMask=VK_COLOR_COMPONENT_R_BIT or VK_COLOR_COMPONENT_G_BIT or VK_COLOR_COMPONENT_B_BIT or VK_COLOR_COMPONENT_A_BIT,
            blendEnable=VK_TRUE,
            srcColorBlendFactor=VK_BLEND_FACTOR_SRC_ALPHA,
            dstColorBlendFactor=VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA,
            colorBlendOp=VK_BLEND_OP_ADD,
            srcAlphaBlendFactor=VK_BLEND_FACTOR_ONE,
            dstAlphaBlendFactor=VK_BLEND_FACTOR_ZERO,
            alphaBlendOp=VK_BLEND_OP_ADD,
        )

        color_blending = VkPipelineColorBlendStateCreateInfo(
            logicOpEnable=VK_FALSE,
            logicOp=VK_LOGIC_OP_COPY,
            attachmentCount=1,
            pAttachments=[color_blend_attachment],
            blendConstants=[0.0, 0.0, 0.0, 0.0],
        )

        pipeline_layout = VkPipelineLayoutCreateInfo(
            setLayoutCount=0,
            pSetLayouts=None,
            pushConstantRangeCount=0,
            pPushConstantRanges=None,
        )

        self._layout = vkCreatePipelineLayout(self._app.device, pipeline_layout, None)

        create_info = VkGraphicsPipelineCreateInfo(
            stageCount=len(self._shaders),
            pStages=stages,
            pVertexInputState=vertex_input_info,
            pInputAssemblyState=input_assembly_info,
            pViewportState=viewport_state,
            pRasterizationState=rasterizer,
            pMultisampleState=multisampling,
            pDepthStencilState=None,
            pColorBlendState=color_blending,
            pDynamicState=dynamic_state_info,
            layout=self._layout,
            renderPass=self._app.render_pass.handle,
            subpass=0,
            basePipelineHandle=VK_NULL_HANDLE,
            basePipelineIndex=-1
        )

        self._handle = vkCreateGraphicsPipelines(self._app.device, VK_NULL_HANDLE, 1, [create_info], None)[0]

        for module in modules:
            vkDestroyShaderModule(self._app.device, module, None)

    def _create_shader_module(self, shader: Shader):
        create_info = VkShaderModuleCreateInfo(
            codeSize = len(shader.data),
            pCode = shader.data
        )

        return vkCreateShaderModule(self._app.device, create_info, None)

    def destroy(self):
        vkDestroyPipeline(self._app.device, self._handle, None)
        vkDestroyPipelineLayout(self._app.device, self._layout, None)
