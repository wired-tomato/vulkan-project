import getopt
import sys

import glfw

from vkproject.graphics.vk_app import VkApp
from vkproject.resources import Resources
from vkproject.resources.shaders import ShaderLoader
from vkproject.windowing import Window


def main():
    args, values = getopt.getopt(sys.argv[1:], "v", ["validate"])

    enable_validation = False
    for arg, value in args:
        if arg in ("-v", "--validate"):
            enable_validation = True

    Resources.register_loader(ShaderLoader())
    Resources.load()

    glfw.init()
    window = Window(800, 800, "title")
    window.hint(glfw.CLIENT_API, glfw.NO_API)
    window.init()

    vk_app = VkApp(window)
    if enable_validation:
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
