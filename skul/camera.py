import game_framework


class Camera:
    def __init__(self):
        self.canvas_width = 1400
        self.canvas_height = 800
        self.x = 0
        self.y = 0
        self.target = None
        self.world_width = 0
        self.world_height = 0

    def set_target_and_world(self, target, w, h):
        self.target = target
        self.world_width = w
        self.world_height = h
        if self.target:
            self.x = clamp(0, int(self.target.x) - self.canvas_width // 2, self.world_width - self.canvas_width)

    def update(self):
        if not self.target:
            return
        target_center_x = int(self.target.x)
        new_x = target_center_x - (self.canvas_width // 2)
        self.x = clamp(0, new_x, self.world_width - self.canvas_width)
        self.y = 0

    def init(self):
        self.x = 0
        self.y = 0
        self.target = None
        self.world_width = 0
        self.world_height = 0


def clamp(minimum, value, maximum):
    return max(minimum, min(value, maximum))


camera = Camera()