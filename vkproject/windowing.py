import glfw


class Window:
    def __init__(self, width, height, name):
        self._width = width
        self._height = height
        self._name = name
        self._handle = None
        self._hints: dict[int, int] = dict()

    def init(self):
        for hint, value in self._hints.items():
            if isinstance(value, str):
                glfw.window_hint_string(hint, value)
            else:
                glfw.window_hint(hint, value)

        self._handle = glfw.create_window(self._width, self._height, self._name, None, None)
        if not self._handle:
            raise RuntimeError("Could not create window")

    def width(self):
        return self._width

    def set_width(self, width):
        self._width = width
        if self._handle:
            glfw.set_window_size(self._handle, width, self._height)

    def height(self):
        return self._height

    def set_height(self, height):
        self._height = height
        if self._handle:
            glfw.set_window_size(self._handle, self._width, height)

    def set_size(self, width, height):
        self._width = width
        self._height = height
        if self._handle:
            glfw.set_window_size(self._handle, width, height)

    def name(self):
        return self._name

    def set_name(self, name):
        self._name = name
        if self._handle:
            glfw.set_window_title(self._handle, self._name)

    def handle(self):
        return self._handle

    def hint(self, hint, value):
        self._hints[hint] = value

    def should_close(self):
        return glfw.window_should_close(self._handle)

    def update(self):
        glfw.poll_events()
