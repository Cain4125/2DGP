from pico2d import *
import game_world
import camera

# python
class Ball:
    image = None

    def __init__(self, x, y, velocity, world_w, scale=3, speed_scale=0.5):
        if Ball.image is None:
            Ball.image = load_image('Skul_Skill.png')
        self.x = x
        self.y = y
        self.velocity = velocity
        self.world_w = world_w
        self.scale = scale
        self.speed_scale = speed_scale
        self.draw_w = int(Ball.image.w * self.scale)
        self.draw_h = int(Ball.image.h * self.scale)

    def draw(self, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        self.image.draw(screen_x, screen_y, self.draw_w, self.draw_h)

    def update(self):
        self.x += self.velocity * self.speed_scale
        if self.x < 0 - self.draw_w / 2 or self.x > self.world_w + self.draw_w / 2:
            game_world.remove_object(self)
