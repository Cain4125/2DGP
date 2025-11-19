from pico2d import load_image, draw_rectangle
import game_framework
from ground import Ground
from constants import *
import game_world


def collide(bb_a, bb_b):
    left_a, bottom_a, right_a, top_a = bb_a
    left_b, bottom_b, right_b, top_b = bb_b
    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False
    return True


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



        dist_x = self.knight.target.x - self.knight.x

        dist_y = abs(self.knight.target.y - self.knight.y)
        is_in_y_range = (dist_y <= 100)



        if abs(dist_x) < DETECT_RANGE and is_in_y_range:
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
        dist_x = self.knight.target.x - self.knight.x
        dist_y = abs(self.knight.target.y - self.knight.y)
        is_in_y_range = (dist_y <= 100)

        if dist_x > 0:
            self.knight.dir = self.knight.face_dir = 1
        else:
            self.knight.dir = self.knight.face_dir = -1

        self.knight.f_frame = (self.knight.f_frame + ENEMY_RUN_FPS * game_framework.frame_time) % 8
        self.knight.frame = int(self.knight.f_frame)
        self.knight.x += self.knight.dir * ENEMY_RUN_SPEED_PPS * game_framework.frame_time

        if abs(dist_x) < ATTACK_RANGE and self.knight.attack_cooldown <= 0:
            self.knight.change_state(self.knight.ATTACK, None)

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
        self.hit_checked = False

    def enter(self, e):
        self.knight.set_sprite_size(self.cell_w, self.cell_h)
        self.knight.f_frame = 0.0
        self.knight.frame = 0
        self.played_once = False
        self.knight.dir = self.knight.face_dir
        self.hold = 0.6
        self.hit_checked = False

    def exit(self):
        pass

    def do(self):
        if not self.played_once:
            self.knight.x += self.knight.dir * ENEMY_ATTACK_MOVE_PPS * game_framework.frame_time

            frame_before = int(self.knight.f_frame)
            self.knight.f_frame += ENEMY_ATTACK_FPS * game_framework.frame_time
            frame_after = int(self.knight.f_frame)

            if not self.hit_checked and frame_after >= 2 and frame_before < 2:
                self.knight.check_attack_collision()
                self.hit_checked = True

            if self.knight.f_frame >= 5.0:
                self.played_once = True
                self.knight.frame = 4
            else:
                self.knight.frame = int(self.knight.f_frame)
        else:
            self.hold -= game_framework.frame_time
            if self.hold <= 0:
                self.knight.attack_cooldown = 3.0

                if self.knight.detected:
                    self.knight.change_state(self.knight.RUN, None)
                    return

                if not self.knight.target:
                    self.knight.change_state(self.knight.IDLE, None)
                    return

                dist = self.knight.target.x - self.knight.x
                if abs(dist) < DETECT_RANGE:
                    self.knight.detected = True
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
        self.anim_duration = 0.0
        self.state_duration = 0.0

    def enter(self, attacker_face_dir):
        self.knight.set_sprite_size(self.cell_w, self.cell_h)
        self.knight.f_frame = 0.0
        self.knight.frame = 0
        if attacker_face_dir:
            self.knight.knockback_dir = attacker_face_dir
        else:
            self.knight.knockback_dir = 0
        self.anim_duration = 2.0 / ENEMY_HIT_FPS
        self.state_duration = 1.3
        self.knight.detected = True

    def exit(self):
        pass

    def do(self):
        self.state_duration -= game_framework.frame_time

        if self.state_duration <= 0:
            if self.knight.detected:
                self.knight.change_state(self.knight.RUN, None)
                return

            if not self.knight.target:
                self.knight.change_state(self.knight.IDLE, None)
                return
            dist = self.knight.target.x - self.knight.x
            if abs(dist) < DETECT_RANGE:
                self.knight.change_state(self.knight.RUN, None)
            else:
                self.knight.change_state(self.knight.IDLE, None)
            return

        if self.anim_duration > 0:
            self.anim_duration -= game_framework.frame_time
            self.knight.f_frame = (self.knight.f_frame + ENEMY_HIT_FPS * game_framework.frame_time) % 2
            self.knight.frame = int(self.knight.f_frame)
            self.knight.x += self.knight.knockback_dir * KNOCKBACK_SPEED_PPS * game_framework.frame_time
        else:
            self.knight.frame = 1

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
        self.detected = False

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

        self.max_hp = ENEMY_KNIGHT_MAX_HP
        self.current_hp = ENEMY_KNIGHT_MAX_HP
        self.alive = True

    def set_sprite_size(self, w, h):
        self.sprite_w = w
        self.sprite_h = h

    def change_state(self, new, e):
        if self.cur_state == new:
            if self.cur_state == self.HIT:
                pass
            else:
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

    def get_attack_bb(self):
        attack_width = 140
        attack_height = 160

        half_sprite = (self.sprite_w / 2.0) * SCALE
        base_offset = half_sprite - 70
        center_x = self.x + base_offset * self.face_dir
        center_y = self.y

        return (center_x - attack_width / 2,
                center_y - attack_height / 2,
                center_x + attack_width / 2,
                center_y + attack_height / 2)

    def check_attack_collision(self):
        from skull import Skull

        if not self.target:
            return

        attack_bb = self.get_attack_bb()

        if isinstance(self.target, Skull):
            if collide(attack_bb, self.target.get_bb()):
                print("KNIGHT HITS SKULL!")
                self.target.take_damage(self.x)

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

    def take_damage(self, damage_amount, attacker_face_dir):
        if not self.alive:
            return

        self.current_hp -= damage_amount
        print(f"KNIGHT HIT! HP: {self.current_hp}")

        if self.current_hp <= 0:
            self.alive = False

            y_offset_to_sink =(self.hit_h * SCALE / 2) - (17 * SCALE / 2) + 7

            dead_knight_body = DeadEnemy(
                self.x,
                self.y - y_offset_to_sink,
                'knight_dead.png',
                72,
                17,
                6.0
            )
            game_world.add_object(dead_knight_body, 0)

        if self.alive:
            self.change_state(self.HIT, attacker_face_dir)

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
        if not self.alive:
            game_world.remove_object(self)
            return

    def draw(self, cx, cy):
        if not self.alive:
            return
        self.cur_state.draw(cx, cy)
        lx, by, rx, ty = self.get_bb()
        #draw_rectangle(lx - cx, by - cy, rx - cx, ty - cy)

        if self.cur_state == self.ATTACK:
            lx, by, rx, ty = self.get_attack_bb()
            #draw_rectangle(lx - cx, by - cy, rx - cx, ty - cy)


class DeadEnemy:

    def __init__(self, x, y, image_name, sprite_w, sprite_h, duration=3.0):
        self.image = load_image(image_name)
        self.x, self.y = x, y
        self.sprite_w = sprite_w
        self.sprite_h = sprite_h
        self.scale = SCALE
        self.timer = duration

    def get_bb(self):
        half_w = (self.sprite_w * self.scale) / 2
        half_h = (self.sprite_h * self.scale) / 2 - 30
        return self.x - half_w, self.y - half_h - 30, self.x + half_w, self.y + half_h

    def update(self):
        self.timer -= game_framework.frame_time
        if self.timer <= 0:
            game_world.remove_object(self)

    def draw(self, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        self.image.draw(screen_x, screen_y, self.sprite_w * self.scale, self.sprite_h * self.scale)