from pico2d import load_image, draw_rectangle
import game_framework
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
        self.knight.set_sprite_size(self.cell_w, self.cell_h)
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
        dist = self.knight.target.x - self.knight.x
        if abs(dist) < ATTACK_RANGE and self.knight.attack_cooldown <= 0:
            self.knight.change_state(self.knight.ATTACK, None)
        elif abs(dist) < DETECT_RANGE:
            self.knight.change_state(self.knight.RUN, None)

    def draw(self, cx, cy):
        sx = self.cell_w * self.knight.frame
        x = self.knight.x - cx
        y_offset = (self.cell_h / 2) - (self.knight.hit_h / 2)
        y = (self.knight.y - cy) + (y_offset * SCALE)
        w = self.knight.sprite_w * SCALE
        h = self.knight.sprite_h * SCALE
        if self.knight.face_dir == 1:
            Idle.image.clip_draw(sx, 0, self.cell_w, self.cell_h, x, y, w, h)
        else:
            Idle.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'h', x, y, w, h)


class Run:
    image = None

    def __init__(self, knight):
        self.knight = knight
        if Run.image is None:
            Run.image = load_image('knight_run.png')
        self.cell_w = 100
        self.cell_h = 50

    def enter(self, e):
        self.knight.set_sprite_size(self.cell_w, self.cell_h)
        self.knight.f_frame = 0.0
        self.knight.frame = 0

    def exit(self):
        pass

    def do(self):
        if not self.knight.target:
            return
        dist = self.knight.target.x - self.knight.x
        if dist > 0:
            self.knight.dir = self.knight.face_dir = 1
        else:
            self.knight.dir = self.knight.face_dir = -1
        self.knight.f_frame = (self.knight.f_frame + ENEMY_RUN_FPS * game_framework.frame_time) % 8
        self.knight.frame = int(self.knight.f_frame)
        self.knight.x += self.knight.dir * ENEMY_RUN_SPEED_PPS * game_framework.frame_time
        if abs(dist) < ATTACK_RANGE and self.knight.attack_cooldown <= 0:
            self.knight.change_state(self.knight.ATTACK, None)
        elif abs(dist) > DETECT_RANGE:
            self.knight.change_state(self.knight.IDLE, None)

    def draw(self, cx, cy):
        sx = self.cell_w * self.knight.frame
        x = self.knight.x - cx
        y_offset = (self.cell_h / 2) - (self.knight.hit_h / 2)
        y = (self.knight.y - cy) + (y_offset * SCALE)
        w = self.knight.sprite_w * SCALE
        h = self.knight.sprite_h * SCALE
        if self.knight.face_dir == 1:
            Run.image.clip_draw(sx, 0, self.cell_w, self.cell_h, x, y, w, h)
        else:
            Run.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'h', x, y, w, h)


class Attack:
    image = None

    def __init__(self, knight):
        self.knight = knight
        if Attack.image is None:
            Attack.image = load_image('knight_attack.png')
        self.cell_w = 100
        self.cell_h = 100
        self.played_once = False
        self.hold = 0.0

    def enter(self, e):
        self.knight.set_sprite_size(self.cell_w, self.cell_h)
        self.knight.f_frame = 0.0
        self.knight.frame = 0
        self.played_once = False
        self.knight.dir = self.knight.face_dir
        self.hold = 0.6

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
            self.hold -= game_framework.frame_time
            if self.hold <= 0:
                self.knight.attack_cooldown = 3.0
                if not self.knight.target:
                    self.knight.change_state(self.knight.IDLE, None)
                    return
                dist = self.knight.target.x - self.knight.x
                if abs(dist) < DETECT_RANGE:
                    self.knight.change_state(self.knight.RUN, None)
                else:
                    self.knight.change_state(self.knight.IDLE, None)

    def draw(self, cx, cy):
        sx = self.cell_w * self.knight.frame
        x = self.knight.x - cx
        y_offset = (self.cell_h / 2) - (self.knight.hit_h / 2)
        y = (self.knight.y - cy) + (y_offset * SCALE)
        w = self.knight.sprite_w * SCALE
        h = self.knight.sprite_h * SCALE
        if self.knight.face_dir == 1:
            Attack.image.clip_draw(sx, 0, self.cell_w, self.cell_h, x, y, w, h)
        else:
            Attack.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'h', x, y, w, h)


class Hit:
    image = None

    def __init__(self, knight):
        self.knight = knight
        if Hit.image is None:
            Hit.image = load_image('knight_hit.png')
        self.cell_w = 50
        self.cell_h = 100
        self.anim = 0.0
        self.hold = 0.0

    def enter(self, attacker_face_dir):
        self.knight.set_sprite_size(self.cell_w, self.cell_h)
        self.knight.f_frame = 0.0
        self.knight.frame = 0
        if attacker_face_dir:
            self.knight.knockback_dir = -attacker_face_dir
        else:
            self.knight.knockback_dir = 0
        self.anim = 2.0 / ENEMY_HIT_FPS
        self.hold = 1.0

    def exit(self):
        pass

    def do(self):
        if self.anim > 0:
            self.anim -= game_framework.frame_time
            self.knight.f_frame = (self.knight.f_frame + ENEMY_HIT_FPS * game_framework.frame_time) % 2
            self.knight.frame = int(self.knight.f_frame)
            self.knight.x += self.knight.knockback_dir * KNOCKBACK_SPEED_PPS * game_framework.frame_time
        elif self.hold > 0:
            self.knight.frame = 1
            self.hold -= game_framework.frame_time
        else:
            if not self.knight.target:
                self.knight.change_state(self.knight.IDLE, None)
                return
            dist = self.knight.target.x - self.knight.x
            if abs(dist) < DETECT_RANGE:
                self.knight.change_state(self.knight.RUN, None)
            else:
                self.knight.change_state(self.knight.IDLE, None)

    def draw(self, cx, cy):
        sx = self.cell_w * self.knight.frame
        x = self.knight.x - cx
        y_offset = (self.cell_h / 2) - (self.knight.hit_h / 2)
        y = (self.knight.y - cy) + (y_offset * SCALE)
        w = self.knight.sprite_w * SCALE
        h = self.knight.sprite_h * SCALE
        if self.knight.face_dir == 1:
            Hit.image.clip_draw(sx, 0, self.cell_w, self.cell_h, x, y, w, h)
        else:
            Hit.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'h', x, y, w, h)


class EnemyKnight:
    class DUMMY_JUMP:
        def enter(self, e): pass
        def exit(self): pass
        def do(self): pass
        def draw(self, cx, cy): pass

    def __init__(self, x, y, target, platforms):
        self.x, self.y = x, y
        self.f_frame = 0.0
        self.frame = 0
        self.face_dir = -1
        self.dir = 0
        self.vy = 0.0
        self.on_ground = True

        self.sprite_w = 50
        self.sprite_h = 100

        self.hit_w = 50
        self.hit_h = 60
        self.half_hit_w = (self.hit_w * SCALE) / 2
        self.half_hit_h = (self.hit_h * SCALE) / 2

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

    def set_sprite_size(self, w, h):
        self.sprite_w = w
        self.sprite_h = h

    def change_state(self, new, e):
        if self.cur_state == new:
            return
        self.cur_state.exit()
        self.cur_state = new
        self.cur_state.enter(e)

    def get_bb(self):
        return (self.x - self.half_hit_w,
                self.y - self.half_hit_h,
                self.x + self.half_hit_w,
                self.y + self.half_hit_h)

    def get_bb_feet(self):
        return (self.x - self.half_hit_w,
                self.y - self.half_hit_h,
                self.x + self.half_hit_w,
                self.y - self.half_hit_h + 5)

    def check_ground(self):
        self.on_ground = False
        feet = self.get_bb_feet()
        for p in self.platforms:
            if not isinstance(p, Ground):
                continue
            b = p.get_bb()
            if feet[2] < b[0]: continue
            if feet[0] > b[2]: continue
            if feet[3] < b[1]: continue
            if feet[1] > b[3]: continue
            if self.vy <= 0:
                self.on_ground = True
                self.vy = 0
                self.y = b[3] + self.half_hit_h
                return

    def take_damage(self, face):
        if self.cur_state != self.HIT:
            self.change_state(self.HIT, face)

    def update(self):
        self.attack_cooldown -= game_framework.frame_time
        if self.cur_state not in (self.ATTACK, self.HIT):
            self.vy -= GRAVITY_PPS * game_framework.frame_time
        self.y += self.vy * game_framework.frame_time
        self.check_ground()
        self.cur_state.do()
        if not self.on_ground:
            hard_y = 60 + self.half_hit_h
            if self.y < hard_y:
                self.y = hard_y
                self.vy = 0
                self.on_ground = True

    def draw(self, cx, cy):
        self.cur_state.draw(cx, cy)
        lx, by, rx, ty = self.get_bb()
        draw_rectangle(lx - cx, by - cy, rx - cx, ty - cy)