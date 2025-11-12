from pico2d import *
import game_world
import camera

class Ball:
    image = None

    def __init__(self, x, y, velocity, world_w):
        if Ball.image is None:
            Ball.image = load_image('ball21x21.png')
        self.x = x
        self.y = y
        self.velocity = velocity
        self.world_w = world_w

    def draw(self, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        self.image.draw(screen_x, screen_y)

    def update(self):
        self.x += self.velocity
        if self.x < 0 or self.x > self.world_w:
            game_world.remove_object(self)