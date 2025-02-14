import glfw

from vk_app import VkApp
from windowing import Window


def main():
    glfw.init()
    window = Window(800, 800, "title")
    window.hint(glfw.CLIENT_API, glfw.NO_API)
    window.init()

    vk_app = VkApp(window)
    # required vulkan SDK - https://vulkan.lunarg.com/
    vk_app.validation_layer("VK_LAYER_KHRONOS_validation")
    vk_app.enable_validation() # comment out this line to run without validation enabled, removes vulkan SDK dependency
    vk_app.create_instance()
    vk_app.setup_debug_messenger()

    while not window.should_close():
        window.update()

    glfw.terminate()
    vk_app.cleanup()

if __name__ == '__main__':
    main()
