from pico2d import load_image, draw_rectangle
from constants import SCALE


class UI:
    def __init__(self, skull):
        self.skull = skull
        self.image_frame = load_image('Ui_frame.png')
        self.image_hp = load_image('hp_bar.png')
        self.icon_a = load_image('A.png')
        self.icon_a_cd = load_image('A_cooldown.png')
        self.icon_s = load_image('S.png')
        self.icon_s_cd = load_image('S_cooldown.png')

        self.w = 108
        self.h = 30

        self.draw_w = self.w * SCALE
        self.draw_h = self.h * SCALE

        self.x = 20 + (self.draw_w / 2)
        self.y = 20 + (self.draw_h / 2)

        self.frame_left = self.x - (self.draw_w / 2) - 10
        self.frame_bottom = self.y - (self.draw_h / 2)

        self.hp_local_x = 38 * SCALE
        self.hp_local_y = 17 * SCALE
        self.hp_full_width = 70 * SCALE
        self.hp_height = 8 * SCALE

        self.skill_y = self.frame_bottom + (7 * SCALE) - 5
        self.skill_a_x = self.frame_left + (48 * SCALE) + 38
        self.skill_s_x = self.frame_left + (80 * SCALE) + 47
        self.icon_size = self.icon_a.w * SCALE / 1.7

        self.hp_current_width = 0
        self.hp_draw_x = 0

    def update(self):
        hp_ratio = max(0, self.skull.current_hp / self.skull.max_hp)
        self.hp_current_width = int(self.hp_full_width * hp_ratio)
        self.hp_draw_x = self.frame_left + self.hp_local_x + (self.hp_current_width / 2)

    def draw(self, camera_x, camera_y):
        self.image_frame.draw(self.x, self.y, self.draw_w, self.draw_h)

        if self.hp_current_width > 0:
            self.image_hp.draw(
                self.hp_draw_x,
                self.frame_bottom + self.hp_local_y,
                self.hp_current_width,
                self.hp_height
            )

        if self.skull.skill_cooldown > 0:
            self.icon_a_cd.draw(self.skill_a_x, self.skill_y, self.icon_size, self.icon_size)
        else:
            self.icon_a.draw(self.skill_a_x, self.skill_y, self.icon_size, self.icon_size)

        if self.skull.skill_s_cooldown > 0:
            self.icon_s_cd.draw(self.skill_s_x, self.skill_y, self.icon_size, self.icon_size)
        else:
            self.icon_s.draw(self.skill_s_x, self.skill_y, self.icon_size, self.icon_size)

    def get_bar_rect(self, x, y, w, h):
        return x, y, x + w, y + h