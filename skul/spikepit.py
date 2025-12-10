from pico2d import load_image, draw_rectangle
import game_framework
import game_world
from constants import SCALE


def collide(bb_a, bb_b):
    left_a, bottom_a, right_a, top_a = bb_a
    left_b, bottom_b, right_b, top_b = bb_b
    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False
    return True


class SpikePit:
    image = None

    def __init__(self, x, y, target, is_ceiling=False):
        if SpikePit.image is None:
            SpikePit.image = load_image('spikepit_idle.png')

        self.x, self.y = x, y
        self.target = target
        self.is_ceiling = is_ceiling

        self.image_w = 1408
        self.image_h = 96
        self.frame_count = 11
        self.cell_w = self.image_w // self.frame_count
        self.cell_h = self.image_h

        self.scale = SCALE
        self.frame = 0
        self.f_frame = 0.0
        self.fps = 10.0

        self.damage = 10

        self.hit_w = self.cell_w * 0.7
        self.hit_h = self.cell_h * 0.5

    def update(self):
        # [애니메이션 업데이트]
        self.f_frame = (self.f_frame + self.fps * game_framework.frame_time) % self.frame_count
        self.frame = int(self.f_frame)

        # [충돌 및 데미지 로직]
        for o in game_world.all_objects():
            if self.is_damageable(o):
                if collide(self.get_bb(), o.get_bb()):

                    # 1. 플레이어 (Skull)
                    if type(o).__name__ == 'Skull':
                        # [수정] 무적 상태가 아닐 때만 넉백과 데미지 적용!
                        # (무적이면 가시 위를 그냥 걸어다닐 수 있음)
                        if o.invincible_timer <= 0:
                            if hasattr(o, 'vy'):
                                o.vy = 500  # 넉백(위로 튕김)
                            o.take_damage(self.damage, self.x)

                    # 2. 적 (Enemy...)
                    elif type(o).__name__.startswith('Enemy'):
                        o.take_damage(self.damage, 0)

    def is_damageable(self, o):
        name = type(o).__name__
        return name == 'Skull' or name.startswith('Enemy')

    def draw(self, camera_x, camera_y):
        sx = self.frame * self.cell_w
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        width = self.cell_w * self.scale
        height = self.cell_h * self.scale

        if self.is_ceiling:
            SpikePit.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'v', screen_x, screen_y, width,
                                               height)
        else:
            SpikePit.image.clip_draw(sx, 0, self.cell_w, self.cell_h, screen_x, screen_y, width, height)

    def get_bb(self):
        half_w = (self.hit_w * self.scale) / 2
        half_h = (self.hit_h * self.scale) / 3 + 10

        if self.is_ceiling:
            bb_offset_y = -40
        else:
            bb_offset_y = 40

        adjusted_y = self.y + bb_offset_y

        return self.x - half_w, adjusted_y - half_h, self.x + half_w, adjusted_y + half_h