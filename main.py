import glfw

from vkproject.graphics.vk_app import VkApp
from vkproject.resources import Resources
from vkproject.resources.shaders import ShaderLoader
from vkproject.windowing import Window
import volk


def load_vk_inst_functions(vk_inst):
    print(f"Loading vk instance functions from instance {vk_inst}")
    volk.lib.volkLoadInstance(vk_inst)

def main():
    Resources.register_loader(ShaderLoader())
    Resources.load()

    volk.lib.volkInitialize()

    glfw.init()
    window = Window(800, 800, "title")
    window.hint(glfw.CLIENT_API, glfw.NO_API)
    window.init()

    vk_app = VkApp(window, load_vk_inst_functions)
    # required vulkan SDK - https://vulkan.lunarg.com/
    vk_app.default_validation_layers()
    vk_app.enable_validation() # comment out this line to run without validation enabled, removes vulkan SDK dependency
    vk_app.init()

    while not window.should_close():
        window.update()
        vk_app.draw_frame()

    glfw.terminate()
    vk_app.cleanup()

if __name__ == '__main__':
    main()
