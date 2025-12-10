from pico2d import load_image, draw_rectangle, clamp, get_time
import game_world
import game_framework
from constants import SCALE, GRAVITY_PPS
import math
import random
import ending_mode

BOSS_SCALE_FACTOR = 1.3
STAMP_SCALE_FACTOR = 0.6


def collide(bb_a, bb_b):
    left_a, bottom_a, right_a, top_a = bb_a
    left_b, bottom_b, right_b, top_b = bb_b
    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False
    return True


class BossDebris:
    images = {}

    def __init__(self, x, y):
        self.x = x
        self.y = y + random.uniform(0, 80)

        self.idx = random.randint(1, 12)
        key = f'part_{self.idx}'
        if key not in BossDebris.images:
            BossDebris.images[key] = load_image(f'boss_dead_part{self.idx:02d}.png')
        self.image = BossDebris.images[key]

        self.vx = random.uniform(-800, 800)
        self.vy = random.uniform(400, 1000)
        self.angle = random.uniform(0, 360)
        self.rotate_speed = random.uniform(-180, 180)
        self.timer = 5.0

    def update(self):
        self.vy -= GRAVITY_PPS * game_framework.frame_time
        self.x += self.vx * game_framework.frame_time
        self.y += self.vy * game_framework.frame_time
        self.angle += self.rotate_speed * game_framework.frame_time
        self.timer -= game_framework.frame_time

        if self.y < 60:
            self.y = 60
            self.vy *= -0.5
            self.vx *= 0.8
            self.rotate_speed = 0

        if self.timer <= 0:
            game_world.remove_object(self)

    def draw(self, cx, cy):
        sx, sy = self.x - cx, self.y - cy
        self.image.composite_draw(math.radians(self.angle), '', sx, sy, self.image.w * SCALE, self.image.h * SCALE)

    def get_bb(self):
        return 0, 0, 0, 0


class BossBall:
    image = None

    def __init__(self, x, y, angle, target, damage=10):
        if BossBall.image is None:
            BossBall.image = load_image('boss_ball.png')
        self.x, self.y = x, y
        self.angle = angle
        self.target = target
        self.speed = 520
        self.damage = damage
        self.r = 15 * SCALE

    def update(self):
        self.x += math.cos(self.angle) * self.speed * game_framework.frame_time
        self.y += math.sin(self.angle) * self.speed * game_framework.frame_time

        if self.x < 0 or self.x > 3000 or self.y < 0 or self.y > 1000:
            game_world.remove_object(self)
            return

        if collide(self.get_bb(), self.target.get_bb()):
            self.target.take_damage(self.damage, self.x)
            game_world.remove_object(self)

    def get_bb(self):
        return self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r

    def draw(self, cx, cy):
        self.image.draw(self.x - cx, self.y - cy, 30 * SCALE, 30 * SCALE)


class BossStamp:
    image = None

    def __init__(self, x, y, skull):
        if BossStamp.image is None:
            BossStamp.image = load_image('boss_stamp.png')
        self.x, self.y = x, y
        self.skull = skull
        self.frame = 0
        self.f_frame = 0.0
        self.fps = 40
        self.total_frames = 22

        self.w = 277 * SCALE * STAMP_SCALE_FACTOR
        self.h = 68 * SCALE * STAMP_SCALE_FACTOR
        self.hit_player = False

    def update(self):
        self.f_frame += self.fps * game_framework.frame_time
        self.frame = int(self.f_frame)

        if not self.hit_player and self.frame < 18:
            if collide(self.get_bb(), self.skull.get_bb()):
                self.skull.take_damage(15, self.x)
                self.hit_player = True

        if self.frame >= self.total_frames:
            game_world.remove_object(self)

    def draw(self, cx, cy):
        sx = self.frame * 277
        self.image.clip_draw(sx, 0, 277, 68, self.x - cx, self.y - cy, self.w, self.h)

    def get_bb(self):
        return self.x - self.w / 2 + (10 * SCALE), self.y - self.h / 2, self.x + self.w / 2 - (
                10 * SCALE), self.y + self.h / 4


class BossIdle:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('boss_idle.png')
        self.w, self.h = 115, 114
        self.frames = 5

    def enter(self):
        self.boss.f_frame = 0.0

    def exit(self):
        pass

    def do(self):
        self.boss.f_frame = (self.boss.f_frame + 8 * game_framework.frame_time) % self.frames
        self.boss.frame = int(self.boss.f_frame)

        if self.boss.attack_cooldown > 0:
            return

        dist_x = abs(self.boss.target.x - self.boss.x)

        is_on_ground = self.boss.target.y < 150

        if dist_x < 180 * SCALE and is_on_ground:
            self.boss.change_state(self.boss.MELEE)
        else:
            self.boss.change_state(self.boss.RANGE)

    def draw(self, cx, cy):
        sx = self.boss.frame * self.w
        draw_w = self.w * SCALE * BOSS_SCALE_FACTOR
        draw_h = self.h * SCALE * BOSS_SCALE_FACTOR
        self.image.clip_draw(sx, 0, self.w, self.h, self.boss.x - cx, self.boss.y - cy, draw_w, draw_h)


class BossMelee:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('boss_melee.png')
        self.w, self.h = 140, 112
        self.frames = 7
        self.phase = 0
        self.timer = 0.0

    def enter(self):
        self.boss.f_frame = 0.0
        self.boss.frame = 0
        self.phase = 0
        self.timer = 0.0

    def exit(self):
        self.boss.attack_cooldown = 3.0

    def do(self):
        if self.phase == 0:
            self.boss.f_frame += 8 * game_framework.frame_time
            if self.boss.f_frame >= 4.0:
                self.boss.f_frame = 3.9
                self.boss.frame = 3
                self.phase = 1
                self.timer = 0.7
            else:
                self.boss.frame = int(self.boss.f_frame)

        elif self.phase == 1:
            self.timer -= game_framework.frame_time
            if self.timer <= 0:
                self.phase = 2
                self.boss.f_frame = 4.0

                stamp_offset = 100 * SCALE
                left_x = self.boss.x - stamp_offset
                right_x = self.boss.x + stamp_offset

                ground_y = 40 + (25 * SCALE)

                game_world.add_object(BossStamp(left_x, ground_y, self.boss.target), 1)
                game_world.add_object(BossStamp(right_x, ground_y, self.boss.target), 1)

        elif self.phase == 2:
            self.boss.f_frame += 10 * game_framework.frame_time
            if self.boss.f_frame >= 7.0:
                self.boss.f_frame = 6.9
                self.boss.frame = 6
                self.phase = 3
                self.timer = 0.3
            else:
                self.boss.frame = int(self.boss.f_frame)

        elif self.phase == 3:
            self.timer -= game_framework.frame_time
            if self.timer <= 0:
                self.boss.change_state(self.boss.IDLE)

    def draw(self, cx, cy):
        sx = self.boss.frame * self.w
        draw_w = self.w * SCALE * BOSS_SCALE_FACTOR
        draw_h = self.h * SCALE * BOSS_SCALE_FACTOR
        self.image.clip_draw(sx, 0, self.w, self.h, self.boss.x - cx, self.boss.y - cy, draw_w, draw_h)


class BossRange:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('boss_range.png')
        self.w, self.h = 134, 115
        self.frames = 4
        self.phase = 0
        self.timer = 0.0

    def enter(self, e=None):
        self.boss.f_frame = 0.0
        self.boss.frame = 0
        self.phase = 0
        self.timer = 0.0

    def exit(self):
        self.boss.attack_cooldown = 3.0

    def do(self):
        if self.phase == 0:
            self.boss.f_frame += 6 * game_framework.frame_time
            if self.boss.f_frame >= 2.0:
                self.boss.f_frame = 1.9
                self.boss.frame = 1
                self.phase = 1
                self.timer = 0.7
            else:
                self.boss.frame = int(self.boss.f_frame)

        elif self.phase == 1:
            self.timer -= game_framework.frame_time
            if self.timer <= 0:
                self.phase = 2
                self.boss.f_frame = 2.0

                center_y = self.boss.y - (10 * SCALE)
                for i in range(8):
                    angle = math.radians(i * 45)
                    ball = BossBall(self.boss.x, center_y, angle, self.boss.target)
                    game_world.add_object(ball, 1)

        elif self.phase == 2:
            self.boss.f_frame += 8 * game_framework.frame_time
            if self.boss.f_frame >= 4.0:
                self.boss.f_frame = 3.9
                self.boss.frame = 3
                self.phase = 3
                self.timer = 0.4
            else:
                self.boss.frame = int(self.boss.f_frame)

        elif self.phase == 3:
            self.timer -= game_framework.frame_time
            if self.timer <= 0:
                self.boss.change_state(self.boss.IDLE)

    def draw(self, cx, cy):
        sx = self.boss.frame * self.w
        draw_w = self.w * SCALE * BOSS_SCALE_FACTOR
        draw_h = self.h * SCALE * BOSS_SCALE_FACTOR
        self.image.clip_draw(sx, 0, self.w, self.h, self.boss.x - cx, self.boss.y - cy, draw_w, draw_h)


class BossDead:
    def __init__(self, boss):
        self.boss = boss
        self.image_dead = load_image('boss_dead.png')
        self.image_dying = load_image('boss_range.png')
        self.dead_w, self.dead_h = 75, 51
        self.dying_w, self.dying_h = 134, 115

        self.timer = 0.0
        self.exploded = False
        self.ending_timer = 4.0

    def enter(self):
        self.timer = 1.5
        self.exploded = False
        self.ending_timer = 4.0

    def exit(self):
        pass

    def do(self):
        if not self.exploded:
            self.timer -= game_framework.frame_time
            if self.timer <= 0:
                self.exploded = True
                # [수정] 12개 -> 24개로 증가 (파편이 더 많이 튐)
                for _ in range(24):
                    debris = BossDebris(self.boss.x, self.boss.y)
                    game_world.add_object(debris, 1)

        self.ending_timer -= game_framework.frame_time
        if self.ending_timer <= 0:
            game_framework.change_mode(ending_mode.EndingMode('CLEAR'))

    def draw(self, cx, cy):
        if not self.exploded:
            sx = 3 * self.dying_w
            draw_w = self.dying_w * SCALE * BOSS_SCALE_FACTOR
            draw_h = self.dying_h * SCALE * BOSS_SCALE_FACTOR
            self.image_dying.clip_draw(sx, 0, self.dying_w, self.dying_h, self.boss.x - cx, self.boss.y - cy, draw_w,
                                       draw_h)
        else:
            draw_w = self.dead_w * SCALE * BOSS_SCALE_FACTOR
            draw_h = self.dead_h * SCALE * BOSS_SCALE_FACTOR
            offset_y = (draw_h / 2) - (114 * SCALE * BOSS_SCALE_FACTOR / 2)
            self.image_dead.draw(self.boss.x - cx, self.boss.y - cy + offset_y, draw_w, draw_h)


class EnemyGiantTree:
    def __init__(self, x, y, target):
        self.x, self.y = x, y
        self.target = target
        self.max_hp = 500
        self.current_hp = self.max_hp
        self.alive = True

        self.IDLE = BossIdle(self)
        self.MELEE = BossMelee(self)
        self.RANGE = BossRange(self)
        self.DEAD = BossDead(self)

        self.cur_state = self.IDLE
        self.frame = 0
        self.f_frame = 0.0

        self.attack_cooldown = 2.0
        self.invincible_timer = 0.0

        self.cur_state.enter()

    def update(self):
        if self.invincible_timer > 0:
            self.invincible_timer -= game_framework.frame_time

        if self.attack_cooldown > 0:
            self.attack_cooldown -= game_framework.frame_time

        self.cur_state.do()
        self.check_collision_with_balls()

    def draw(self, cx, cy):
        self.cur_state.draw(cx, cy)

    def change_state(self, state):
        self.cur_state.exit()
        self.cur_state = state
        self.cur_state.enter()

    def get_bb(self):
        w = 100 * SCALE * BOSS_SCALE_FACTOR
        h = 110 * SCALE * BOSS_SCALE_FACTOR
        return self.x - w / 2, self.y - h / 2, self.x + w / 2, self.y + h / 2

    def take_damage(self, damage, attacker_x=None):
        if not self.alive or self.invincible_timer > 0:
            return

        self.current_hp -= damage
        self.invincible_timer = 0.2
        print(f"BOSS HP: {self.current_hp}")

        if self.current_hp <= 0:
            self.alive = False
            self.change_state(self.DEAD)

    def check_collision_with_balls(self):
        pass