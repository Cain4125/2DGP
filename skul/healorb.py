from pico2d import load_image, draw_rectangle
import game_world
import game_framework
from constants import SCALE
import math


def collide(bb_a, bb_b):
    left_a, bottom_a, right_a, top_a = bb_a
    left_b, bottom_b, right_b, top_b = bb_b
    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False
    return True


class HealOrb:
    image = None

    def __init__(self, x, y, target):
        if HealOrb.image is None:
            HealOrb.image = load_image('healorb.png')

        self.x = x
        self.base_y = y + ((5 * SCALE) / 3)
        self.y = self.base_y
        self.target = target

        self.timer = 0.0
        self.bobbing_speed = 4.0
        self.bobbing_range = 2.0 * SCALE

        self.heal_amount = 10
        self.w, self.h = 15, 15

        self.collect_wait_timer = 1.5

    def update(self):
        self.timer += game_framework.frame_time
        self.collect_wait_timer -= game_framework.frame_time

        self.y = self.base_y + math.sin(self.timer * self.bobbing_speed) * self.bobbing_range

        if self.collect_wait_timer <= 0:
            if collide(self.get_bb(), self.target.get_bb()):
                self.apply_heal()
                game_world.remove_object(self)

    def draw(self, cx, cy):
        width = self.w * SCALE
        height = self.h * SCALE
        self.image.draw(self.x - cx, self.y - cy - 60, width, height)

    def get_bb(self):
        half_w = (self.w * SCALE) / 2
        half_h = (self.h * SCALE) / 2
        return self.x - half_w, self.y - half_h, self.x + half_w, self.y + half_h

    def apply_heal(self):
        self.target.current_hp += self.heal_amount
        if self.target.current_hp > self.target.max_hp:
            self.target.current_hp = self.target.max_hp
        print(f"Healed! HP: {self.target.current_hp}")