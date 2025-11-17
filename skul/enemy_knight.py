from pico2d import load_image, draw_rectangle
import game_framework
import game_world
import camera
from ground import Ground
from constants import *


class Idle:
    image = None

    def __init__(self, knight):
        self.knight = knight
        if Idle.image is None:
            Idle.image = load_image('knight_idle.png')
        self.cell_w = 50
        self.cell_h = 100

    def enter(self, e):
        self.knight.f_frame = 0.0
        self.knight.frame = 0
        self.knight.dir = 0

    def exit(self):
        pass

    def do(self):
        self.knight.f_frame = (self.knight.f_frame + ENEMY_IDLE_FPS * game_framework.frame_time) % 5
        self.knight.frame = int(self.knight.f_frame)
        if not self.knight.target:
            return
        dist_x = self.knight.target.x - self.knight.x
        if abs(dist_x) < ATTACK_RANGE and self.knight.attack_cooldown <= 0:
            self.knight.change_state(self.knight.ATTACK, None)
        elif abs(dist_x) < DETECT_RANGE:
            self.knight.change_state(self.knight.RUN, None)

    def draw(self, camera_x, camera_y):
        sx = self.cell_w * self.knight.frame
        screen_x = self.knight.x - camera_x
        screen_y = self.knight.y - camera_y
        if self.knight.face_dir == 1:
            Idle.image.clip_draw(sx, 0, self.cell_w, self.cell_h, screen_x, screen_y, self.cell_w * SCALE, self.cell_h * SCALE)
        else:
            Idle.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'h', screen_x, screen_y, self.cell_w * SCALE, self.cell_h * SCALE)


class Run:
    image = None

    def __init__(self, knight):
        self.knight = knight
        if Run.image is None:
            Run.image = load_image('knight_run.png')
        self.cell_w = 100
        self.cell_h = 50

    def enter(self, e):
        self.knight.f_frame = 0.0
        self.knight.frame = 0

    def exit(self):
        pass

    def do(self):
        if not self.knight.target:
            return
        dist_x = self.knight.target.x - self.knight.x
        if dist_x > 0:
            self.knight.dir = self.knight.face_dir = 1
        else:
            self.knight.dir = self.knight.face_dir = -1
        self.knight.f_frame = (self.knight.f_frame + ENEMY_RUN_FPS * game_framework.frame_time) % 8
        self.knight.frame = int(self.knight.f_frame)
        self.knight.x += self.knight.dir * ENEMY_RUN_SPEED_PPS * game_framework.frame_time
        if abs(dist_x) < ATTACK_RANGE and self.knight.attack_cooldown <= 0:
            self.knight.change_state(self.knight.ATTACK, None)
        elif abs(dist_x) > DETECT_RANGE:
            self.knight.change_state(self.knight.IDLE, None)

    def draw(self, camera_x, camera_y):
        sx = self.cell_w * self.knight.frame
        screen_x = self.knight.x - camera_x
        y_offset = (50 * SCALE) / 2
        draw_y = self.knight.y - y_offset
        screen_y = draw_y - camera_y
        if self.knight.face_dir == 1:
            Run.image.clip_draw(sx, 0, self.cell_w, self.cell_h, screen_x, screen_y, self.cell_w * SCALE, self.cell_h * SCALE)
        else:
            Run.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'h', screen_x, screen_y, self.cell_w * SCALE, self.cell_h * SCALE)


class Attack:
    image = None

    def __init__(self, knight):
        self.knight = knight
        if Attack.image is None:
            Attack.image = load_image('knight_attack.png')
        self.cell_w = 100
        self.cell_h = 100
        self.played_once = False
        self.hold_timer = 0.0

    def enter(self, e):
        self.knight.f_frame = 0.0
        self.knight.frame = 0
        self.knight.dir = self.knight.face_dir
        self.played_once = False
        self.hold_timer = 0.6

    def exit(self):
        pass

    def do(self):
        if not self.played_once:
            self.knight.x += self.knight.dir * ENEMY_ATTACK_MOVE_PPS * game_framework.frame_time
            self.knight.f_frame += ENEMY_ATTACK_FPS * game_framework.frame_time
            if self.knight.f_frame >= 5.0:
                self.played_once = True
                self.knight.frame = 4
            else:
                self.knight.frame = int(self.knight.f_frame)
        else:
            self.hold_timer -= game_framework.frame_time
            if self.hold_timer <= 0:
                self.knight.attack_cooldown = 3.0
                if not self.knight.target:
                    self.knight.change_state(self.knight.IDLE, None)
                    return
                dist_x = self.knight.target.x - self.knight.x
                if abs(dist_x) < DETECT_RANGE:
                    self.knight.change_state(self.knight.RUN, None)
                else:
                    self.knight.change_state(self.knight.IDLE, None)

    def draw(self, camera_x, camera_y):
        sx = self.cell_w * self.knight.frame
        screen_x = self.knight.x - camera_x
        screen_y = self.knight.y - camera_y
        if self.knight.face_dir == 1:
            Attack.image.clip_draw(sx, 0, self.cell_w, self.cell_h, screen_x, screen_y, self.cell_w * SCALE, self.cell_h * SCALE)
        else:
            Attack.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'h', screen_x, screen_y, self.cell_w * SCALE, self.cell_h * SCALE)


class Hit:
    image = None

    def __init__(self, knight):
        self.knight = knight
        if Hit.image is None:
            Hit.image = load_image('knight_hit.png')
        self.cell_w = 50
        self.cell_h = 100
        self.anim_timer = 0.0
        self.hold_timer = 0.0

    def enter(self, attacker_face_dir):
        self.knight.f_frame = 0.0
        self.knight.frame = 0
        self.knight.dir = 0
        if attacker_face_dir:
            self.knight.knockback_dir = -attacker_face_dir
        else:
            self.knight.knockback_dir = 0
        self.anim_timer = (2.0 / ENEMY_HIT_FPS)
        self.hold_timer = 1.0

    def exit(self):
        pass

    def do(self):
        if self.anim_timer > 0:
            self.anim_timer -= game_framework.frame_time
            self.knight.f_frame = (self.knight.f_frame + ENEMY_HIT_FPS * game_framework.frame_time) % 2
            self.knight.frame = int(self.knight.f_frame)
            self.knight.x += self.knight.knockback_dir * KNOCKBACK_SPEED_PPS * game_framework.frame_time
        elif self.hold_timer > 0:
            self.knight.frame = 1
            self.hold_timer -= game_framework.frame_time
        else:
            if not self.knight.target:
                self.knight.change_state(self.knight.IDLE, None)
                return
            dist_x = self.knight.target.x - self.knight.x
            if abs(dist_x) < DETECT_RANGE:
                self.knight.change_state(self.knight.RUN, None)
            else:
                self.knight.change_state(self.knight.IDLE, None)

    def draw(self, camera_x, camera_y):
        sx = self.cell_w * self.knight.frame
        screen_x = self.knight.x - camera_x
        screen_y = self.knight.y - camera_y
        if self.knight.face_dir == 1:
            Hit.image.clip_draw(sx, 0, self.cell_w, self.cell_h, screen_x, screen_y, self.cell_w * SCALE, self.cell_h * SCALE)
        else:
            Hit.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'h', screen_x, screen_y, self.cell_w * SCALE, self.cell_h * SCALE)


class EnemyKnight:
    class DUMMY_JUMP:
        def enter(self, e):
            pass
        def exit(self):
            pass
        def do(self):
            pass
        def draw(self, camera_x, camera_y):
            pass

    def __init__(self, x, y, target, platforms):
        self.x, self.y = x, y
        self.f_frame = 0.0
        self.frame = 0
        self.face_dir = -1
        self.dir = 0
        self.vy = 0.0
        self.on_ground = True
        self.cell_w = 50
        self.cell_h = 50
        self.half_w = (self.cell_w * SCALE) / 2
        self.half_h = (self.cell_h * SCALE) / 2
        self.target = target
        self.platforms = platforms
        self.attack_cooldown = 0.0
        self.knockback_dir = 0
        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.ATTACK = Attack(self)
        self.HIT = Hit(self)
        self.JUMP = self.DUMMY_JUMP()
        self.cur_state = self.IDLE
        self.cur_state.enter(None)

    def change_state(self, new_state, e):
        if self.cur_state == new_state:
            return
        self.cur_state.exit()
        self.cur_state = new_state
        self.cur_state.enter(e)

    def get_bb_feet(self):
        return self.x - self.half_w, self.y - self.half_h, self.x + self.half_w, self.y - self.half_h + 5

    def get_bb(self):
        return self.x - self.half_w, self.y - self.half_h, self.x + self.half_w, self.y + self.half_h

    def check_ground(self):
        self.on_ground = False
        my_feet = self.get_bb_feet()
        if not self.platforms:
            return
        for p in self.platforms:
            if not isinstance(p, Ground):
                continue
            platform_bb = p.get_bb()
            left_a, bottom_a, right_a, top_a = my_feet
            left_b, bottom_b, right_b, top_b = platform_bb
            if left_a > right_b:
                continue
            if right_a < left_b:
                continue
            if top_a < bottom_b:
                continue
            if bottom_a > top_b:
                continue
            if self.vy <= 0:
                self.on_ground = True
                self.vy = 0
                self.y = platform_bb[3] + self.half_h
                return

    def take_damage(self, attacker_face_dir):
        if self.cur_state != self.HIT:
            self.change_state(self.HIT, attacker_face_dir)

    def update(self):
        self.attack_cooldown -= game_framework.frame_time
        cur = self.cur_state
        if cur not in (self.ATTACK, self.HIT):
            self.vy -= GRAVITY_PPS * game_framework.frame_time
        self.y += self.vy * game_framework.frame_time
        self.check_ground()
        self.cur_state.do()
        cur_after_do = self.cur_state
        if self.on_ground:
            pass
        else:
            if cur_after_do in (self.IDLE, self.RUN):
                self.check_ground()
        if not self.on_ground:
            hard_floor_y = 60 + self.half_h
            if self.y < hard_floor_y:
                self.y = hard_floor_y
                self.vy = 0
                self.on_ground = True

    def draw(self, camera_x, camera_y):
        self.cur_state.draw(camera_x, camera_y)
        lx, by, rx, ty = self.get_bb()
        draw_rectangle(lx - camera_x, by - camera_y, rx - camera_x, ty - camera_y)