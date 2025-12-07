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

    def update(self):
        pass

    def draw(self, camera_x, camera_y):
        self.image_frame.draw(self.x, self.y, self.w * SCALE, self.h * SCALE)
        hp_local_x = 38 * SCALE
        hp_local_y = 17 * SCALE
        hp_full_width = 70 * SCALE
        hp_height = 8 * SCALE
        hp_ratio = max(0, self.skull.current_hp / self.skull.max_hp)
        hp_current_width = int(hp_full_width * hp_ratio)
        frame_left = self.x - (self.w * SCALE / 2) - 10
        frame_bottom = self.y - (self.h * SCALE / 2)
        if hp_current_width > 0:
            self.image_hp.draw(
                frame_left + hp_local_x + (hp_current_width / 2),
                frame_bottom + hp_local_y,
                hp_current_width,
                hp_height
            )

        skill_y = frame_bottom + (7 * SCALE) - 5
        skill_a_x = frame_left + (48 * SCALE) + 38
        skill_s_x = frame_left + (80 * SCALE) + 47
        icon_size = self.icon_a.w * SCALE/1.7
        if self.skull.skill_cooldown > 0:
            self.icon_a_cd.draw(skill_a_x, skill_y, icon_size, icon_size)
        else:
            self.icon_a.draw(skill_a_x, skill_y, icon_size, icon_size)

        if self.skull.skill_s_cooldown > 0:
            self.icon_s_cd.draw(skill_s_x, skill_y, icon_size, icon_size)
        else:
            self.icon_s.draw(skill_s_x, skill_y, icon_size, icon_size)

    def get_bar_rect(self, x, y, w, h):
        return x, y, x + w, y + h