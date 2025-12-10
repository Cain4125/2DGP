from pico2d import load_image, get_time, draw_rectangle, clamp
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_RIGHT, SDLK_LEFT, SDLK_DOWN, SDLK_a, SDLK_s, SDLK_z, SDLK_x


import game_world
import game_framework
from state_machine import StateMachine
from ball import Ball
from constants import *
from enemy_knight import EnemyKnight
import lobby_mode
import play_mode

def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a

def s_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_s

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def z_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_z


def x_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_x


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

    def __init__(self, skull):
        self.skull = skull
        if Idle.image is None:
            Idle.image = load_image('skul_idle.png')

    def enter(self, e):
        self.skull.dir = 0
        self.skull.f_frame = 0.0

    def exit(self, e):
        if a_down(e): self.skull.fire_ball()

    def do(self):
        self.skull.recompute_dir()
        if self.skull.dir != 0:
            self.skull.state_machine.cur_state.exit(('AUTO_RUN', None))
            self.skull.state_machine.cur_state = self.skull.RUN
            self.skull.RUN.enter(('AUTO_RUN', None))
            return
        self.skull.f_frame = (self.skull.f_frame + IDLE_FPS * game_framework.frame_time) % 4
        self.skull.frame = int(self.skull.f_frame)

    def draw(self, camera_x, camera_y):
        src_w, src_h = 50, 50
        screen_x = self.skull.x - camera_x
        screen_y = self.skull.y - camera_y
        if self.skull.face_dir == 1:
            Idle.image.clip_draw(self.skull.frame * src_w, 0, src_w, src_h, screen_x, screen_y, src_w * SCALE,
                                 src_h * SCALE)
        else:
            Idle.image.clip_composite_draw(self.skull.frame * src_w, 0, src_w, src_h, 0, 'h', screen_x, screen_y,
                                           src_w * SCALE, src_h * SCALE)

    def handle_event(self, e):
        return False


class Run:
    image = None

    def __init__(self, skull):
        self.skull = skull
        if Run.image is None:
            Run.image = load_image('skul_run.png')

    def enter(self, e):
        self.skull.recompute_dir()
        if self.skull.dir == 0:
            if right_down(e):
                self.skull.dir = 1
            elif left_down(e):
                self.skull.dir = -1
            else:
                self.skull.dir = self.skull.face_dir
        if self.skull.dir != 0: self.skull.face_dir = self.skull.dir
        self.skull.f_frame = 0.0

    def exit(self, e):
        if a_down(e): self.skull.fire_ball()

    def do(self):
        self.skull.f_frame = (self.skull.f_frame + RUN_FPS * game_framework.frame_time) % 8
        self.skull.frame = int(self.skull.f_frame)
        self.skull.recompute_dir()
        self.skull.x += self.skull.dir * RUN_SPEED_PPS * game_framework.frame_time
        if self.skull.dir != 0: self.skull.face_dir = self.skull.dir
        if not (self.skull.left_pressed or self.skull.right_pressed):
            self.skull.state_machine.cur_state.exit(('STOP', None))
            self.skull.state_machine.cur_state = self.skull.IDLE
            self.skull.IDLE.enter(('STOP', None))

    def draw(self, camera_x, camera_y):
        screen_x = self.skull.x - camera_x
        screen_y = self.skull.y - camera_y
        if self.skull.face_dir == 1:
            Run.image.clip_draw(self.skull.frame * 50, 0, 50, 50, screen_x, screen_y, 50 * SCALE, 50 * SCALE)
        else:
            Run.image.clip_composite_draw(self.skull.frame * 50, 0, 50, 50, 0, 'h', screen_x, screen_y, 50 * SCALE,
                                          50 * SCALE)

    def handle_event(self, e):
        return False


class Jump:
    image = None

    def __init__(self, skull):
        self.skull = skull
        if Jump.image is None:
            Jump.image = load_image('skul_jump.png')
        self.cell_w = Jump.image.w // 4
        self.cell_h = Jump.image.h
        self.timer = 0.0
        self.frame_idx = 0

    def enter(self, e):
        if space_down(e):
            if self.skull.down_pressed and self.skull.y > 150:
                self.skull.y -= 50
            elif self.skull.jump_count < 2:
                self.skull.vy = JUMP_VY_PPS
                self.skull.jump_count += 1
        elif e[0] == 'FALL':
            self.skull.jump_count = 1
        self.timer = 0.0

    def exit(self, e):
        if a_down(e): self.skull.fire_ball()

    def do(self):
        self.skull.recompute_dir()
        if self.skull.dir != 0: self.skull.face_dir = self.skull.dir
        self.skull.x += self.skull.dir * RUN_SPEED_PPS * game_framework.frame_time
        self.timer += game_framework.frame_time
        anim_frame = int(self.timer * JUMP_FPS) % 2
        self.frame_idx = (0 + anim_frame) if self.skull.vy > 0 else (2 + anim_frame)

    def draw(self, camera_x, camera_y):
        sx = self.cell_w * self.frame_idx
        sy = 0
        sw = self.cell_w
        sh = self.cell_h
        screen_x = self.skull.x - camera_x
        screen_y = self.skull.y - camera_y
        if self.skull.face_dir == 1:
            Jump.image.clip_draw(sx, sy, sw, sh, screen_x, screen_y, sw * SCALE, sh * SCALE)
        else:
            Jump.image.clip_composite_draw(sx, sy, sw, sh, 0, 'h', screen_x, screen_y, sw * SCALE, sh * SCALE)

    def handle_event(self, e):
        return False


class Dash:
    image = None

    def __init__(self, skull):
        self.skull = skull
        if Dash.image is None:
            Dash.image = load_image('skul_dash.png')
        self.cell_w = Dash.image.w
        self.cell_h = Dash.image.h
        self.timer = 0.0
        self.was_airborne = False

    def enter(self, e):
        self.skull.dir = self.skull.face_dir
        self.timer = 0.0
        self.was_airborne = not self.skull.on_ground
        self.skull.vy = 0
        self.skull.last_dash_time = get_time()
        self.skull.invincible_timer = DASH_DURATION_SEC

    def exit(self, e):
        pass

    def do(self):
        self.skull.x += self.skull.dir * DASH_SPEED_PPS * game_framework.frame_time
        self.timer += game_framework.frame_time
        if self.timer >= DASH_DURATION_SEC:
            self.skull.state_machine.cur_state.exit(('DASH_END', None))
            if self.was_airborne:
                next_state = self.skull.JUMP
            else:
                self.skull.recompute_dir()
                next_state = self.skull.RUN if self.skull.dir != 0 else self.skull.IDLE
            self.skull.state_machine.cur_state = next_state
            next_state.enter(('DASH_END', None))

    def draw(self, camera_x, camera_y):
        screen_x = self.skull.x - camera_x
        screen_y = self.skull.y - camera_y
        if self.skull.face_dir == 1:
            Dash.image.clip_draw(0, 0, self.cell_w, self.cell_h, screen_x, screen_y, self.cell_w * SCALE,
                                 self.cell_h * SCALE)
        else:
            Dash.image.clip_composite_draw(0, 0, self.cell_w, self.cell_h, 0, 'h', screen_x, screen_y,
                                           self.cell_w * SCALE, self.cell_h * SCALE)

    def handle_event(self, e):
        return False


class Attack1:
    image = None

    def __init__(self, skull):
        self.skull = skull
        if Attack1.image is None:
            Attack1.image = load_image('skul_attack.png')
        self.cell_w = 100
        self.cell_h = 100
        self.buffered_x = False
        self.attack_move_dir = 0
        self.hit_enemies = []

    def enter(self, e):
        self.skull.f_frame = 0.0
        self.skull.frame = 0
        self.buffered_x = False
        self.attack_move_dir = self.skull.face_dir
        if not self.skull.on_ground:
            self.skull.vy = 0
        self.hit_enemies.clear()

    def exit(self, e):
        pass

    def do(self):
        if 2 <= self.skull.frame <= 4:
            self.skull.check_attack_collision(self.hit_enemies)
        self.skull.recompute_dir()
        if self.skull.dir != 0 and self.skull.dir != self.attack_move_dir:
            self.attack_move_dir = self.skull.dir
        self.skull.x += self.attack_move_dir * ATTACK_MOVE_PPS * game_framework.frame_time
        self.skull.f_frame += ATTACK_FPS * game_framework.frame_time
        self.skull.frame = int(self.skull.f_frame)

        if self.skull.f_frame >= 5.0:
            self.skull.state_machine.cur_state.exit(('ATTACK1_END', None))
            if self.buffered_x:
                next_state = self.skull.ATTACK2
            elif not self.skull.on_ground:
                next_state = self.skull.JUMP
            else:
                self.skull.recompute_dir()
                next_state = self.skull.RUN if self.skull.dir != 0 else self.skull.IDLE
            self.skull.state_machine.cur_state = next_state
            next_state.enter(('ATTACK1_END', None))

    def draw(self, camera_x, camera_y):
        draw_y = self.skull.y + (25 * SCALE)
        frame_to_draw = min(self.skull.frame, 4)
        sx = self.cell_w * frame_to_draw
        screen_x = self.skull.x - camera_x
        screen_y = draw_y - camera_y
        if self.skull.face_dir == 1:
            Attack1.image.clip_draw(sx, 0, self.cell_w, self.cell_h, screen_x, screen_y, self.cell_w * SCALE,
                                    self.cell_h * SCALE)
        else:
            Attack1.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'h', screen_x, screen_y,
                                              self.cell_w * SCALE, self.cell_h * SCALE)

    def handle_event(self, e):
        if x_down(e):
            self.buffered_x = True
            return True
        return False


class Attack2:
    def __init__(self, skull):
        self.skull = skull
        self.image = Attack1.image
        self.cell_w = 100
        self.cell_h = 100
        self.buffered_x = False
        self.attack_move_dir = 0
        self.hit_enemies = []

    def enter(self, e):
        self.skull.f_frame = 5.0
        self.skull.frame = 5
        self.buffered_x = False
        self.attack_move_dir = self.skull.face_dir
        if not self.skull.on_ground:
            self.skull.vy = 0
        self.hit_enemies.clear()

    def exit(self, e):
        pass

    def do(self):
        if 6 <= self.skull.frame <= 8:
            self.skull.check_attack_collision(self.hit_enemies)
        self.skull.recompute_dir()
        if self.skull.dir != 0 and self.skull.dir != self.attack_move_dir:
            self.attack_move_dir = self.skull.dir
        self.skull.x += self.attack_move_dir * ATTACK_MOVE_PPS * game_framework.frame_time
        self.skull.f_frame += ATTACK_FPS * game_framework.frame_time
        self.skull.frame = int(self.skull.f_frame)

        if self.skull.f_frame >= 9.0:
            self.skull.state_machine.cur_state.exit(('ATTACK2_END', None))
            if self.buffered_x:
                next_state = self.skull.ATTACK1
            elif not self.skull.on_ground:
                next_state = self.skull.JUMP
            else:
                self.skull.recompute_dir()
                next_state = self.skull.RUN if self.skull.dir != 0 else self.skull.IDLE
            self.skull.state_machine.cur_state = next_state
            next_state.enter(('ATTACK2_END', None))

    def draw(self, camera_x, camera_y):
        draw_y = self.skull.y + (25 * SCALE)
        frame_to_draw = min(self.skull.frame, 8)
        sx = self.cell_w * frame_to_draw
        screen_x = self.skull.x - camera_x
        screen_y = draw_y - camera_y
        if self.skull.face_dir == 1:
            self.image.clip_draw(sx, 0, self.cell_w, self.cell_h, screen_x, screen_y, self.cell_w * SCALE,
                                 self.cell_h * SCALE)
        else:
            self.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'h', screen_x, screen_y,
                                           self.cell_w * SCALE, self.cell_h * SCALE)

    def handle_event(self, e):
        if x_down(e):
            self.buffered_x = True
            return True
        return False


class JumpAttack:
    image = None

    def __init__(self, skull):
        self.skull = skull
        if JumpAttack.image is None:
            JumpAttack.image = load_image('skul_jump_attack.png')
        self.cell_w = 100
        self.cell_h = 100
        self.played_once = False
        self.hit_enemies = []

    def enter(self, e):
        self.skull.f_frame = 0.0
        self.skull.frame = 0
        self.played_once = False
        self.hit_enemies.clear()

    def exit(self, e):
        pass

    def do(self):
        if 1 <= self.skull.frame <= 3:
            self.skull.check_attack_collision(self.hit_enemies)
        self.skull.recompute_dir()
        if self.skull.dir != 0:
            self.skull.face_dir = self.skull.dir
        self.skull.x += self.skull.dir * RUN_SPEED_PPS * game_framework.frame_time

        if not self.played_once:
            self.skull.f_frame += JUMP_ATTACK_FPS * game_framework.frame_time
            if self.skull.f_frame >= 4.0:
                self.played_once = True
                self.skull.frame = 3
            else:
                self.skull.frame = int(self.skull.f_frame)
        else:
            self.skull.frame = 3

        if self.played_once and self.skull.on_ground:
            self.skull.state_machine.cur_state.exit(('LAND_ATTACK_END', None))
            self.skull.recompute_dir()
            next_state = self.skull.RUN if (self.skull.left_pressed or self.skull.right_pressed) else self.skull.IDLE
            self.skull.state_machine.cur_state = next_state
            next_state.enter(('LAND_ATTACK_END', None))

    def draw(self, camera_x, camera_y):
        draw_y = self.skull.y + (25 * SCALE)
        frame_to_draw = self.skull.frame
        sx = self.cell_w * frame_to_draw
        screen_x = self.skull.x - camera_x
        screen_y = draw_y - camera_y
        if self.skull.face_dir == 1:
            JumpAttack.image.clip_draw(sx, 0, self.cell_w, self.cell_h, screen_x, screen_y, self.cell_w * SCALE,
                                       self.cell_h * SCALE)
        else:
            JumpAttack.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'h', screen_x, screen_y,
                                                 self.cell_w * SCALE, self.cell_h * SCALE)

    def handle_event(self, e):
        return False


class SkillSpin:
    image = None

    def __init__(self, skull):
        self.skull = skull
        if SkillSpin.image is None:
            SpinImage = load_image('skul_spin.png')
            SkillSpin.image = SpinImage

        self.frame_w = 66
        self.frame_h = 54
        self.frame_count = 7
        self.fps = 15.0

        self.velocity = RUN_SPEED_PPS * 1.3

        self.duration = 2.0
        self.timer = 0.0

        self.hit_interval = 0.3
        self.hit_timer = 0.0
        self.hit_enemies = []

    def enter(self, e):
        self.timer = 1.7
        self.hit_timer = 0.0
        self.hit_enemies.clear()

        self.skull.skill_s_cooldown = 9.0

        self.skull.dir = self.skull.face_dir
        self.skull.vy = 0

    def exit(self, e):
        pass

    def do(self):
        self.skull.x += self.skull.face_dir * self.velocity * game_framework.frame_time

        self.skull.f_frame = (self.skull.f_frame + self.fps * game_framework.frame_time) % self.frame_count
        self.skull.frame = int(self.skull.f_frame)

        self.timer -= game_framework.frame_time
        if self.timer <= 0:
            self.skull.state_machine.cur_state.exit(('TIME_OUT', None))
            self.skull.recompute_dir()
            if self.skull.left_pressed or self.skull.right_pressed:
                next_state = self.skull.RUN
            else:
                next_state = self.skull.IDLE
            self.skull.state_machine.cur_state = next_state
            next_state.enter(('TIME_OUT', None))
            return

        self.hit_timer += game_framework.frame_time
        if self.hit_timer >= self.hit_interval:
            self.hit_timer = 0.0
            self.hit_enemies.clear()


        attack_bb = self.get_attack_bb()
        for o in game_world.all_objects():
            if type(o).__name__ in ('EnemyKnight', 'EnemyTree', 'EnemyGreenTree', 'EnemyGiantTree'):
                if id(o) in self.hit_enemies: continue

                if collide(attack_bb, o.get_bb()):
                    o.take_damage(5, self.skull.face_dir)
                    self.hit_enemies.append(id(o))

    def draw(self, cx, cy):
        sx = self.frame_w * self.skull.frame
        screen_x = self.skull.x - cx
        screen_y = self.skull.y - cy

        w = self.frame_w * SCALE
        h = self.frame_h * SCALE

        if self.skull.face_dir == 1:
            SkillSpin.image.clip_draw(sx, 0, self.frame_w, self.frame_h, screen_x, screen_y, w, h)
        else:
            SkillSpin.image.clip_composite_draw(sx, 0, self.frame_w, self.frame_h, 0, 'h', screen_x, screen_y, w, h)

    def get_attack_bb(self):
        w = self.frame_w * SCALE
        h = self.frame_h * SCALE
        return self.skull.x - w / 2, self.skull.y - h / 2, self.skull.x + w / 2, self.skull.y + h / 2

    def handle_event(self, e):
        return False

class Skull:
    def __init__(self, platforms, world_w=1400):
        self.x, self.y = 400, GROUND_Y
        self.f_frame = 0.0
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.vy = 0.0
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.last_dash_time = 0.0
        self.platforms = platforms
        self.on_ground = True
        self.half_w = (50 * SCALE) / 2
        self.half_h = (50 * SCALE) / 2

        self.world_w = world_w
        self.jump_count = 0

        self.invincible_timer = 0.0

        self.skill_cooldown = 0.0
        self.skill_s_cooldown = 0.0

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.JUMP = Jump(self)
        self.DASH = Dash(self)
        self.ATTACK1 = Attack1(self)
        self.ATTACK2 = Attack2(self)
        self.JUMP_ATTACK = JumpAttack(self)
        self.max_hp = SKULL_MAX_HP
        self.current_hp = SKULL_MAX_HP
        self.hp_bar_image = load_image('hp.png')
        self.down_pressed = False
        self.SKILL_SPIN = SkillSpin(self)

        def z_down_with_cooldown(e):
            is_z = z_down(e)
            cooldown_ready = (get_time() - self.last_dash_time > DASH_COOLDOWN_SEC)
            return is_z and cooldown_ready

        def s_down_ready(e):
            return s_down(e) and self.skill_s_cooldown <= 0

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {z_down_with_cooldown: self.DASH, space_down: self.JUMP, x_down: self.ATTACK1,
                            right_down: self.RUN, left_down: self.RUN, right_up: self.IDLE, left_up: self.IDLE,
                            a_down: self.IDLE, s_down_ready: self.SKILL_SPIN},
                self.RUN: {z_down_with_cooldown: self.DASH, space_down: self.JUMP, x_down: self.ATTACK1,
                           right_down: self.RUN, left_down: self.RUN, right_up: self.RUN, left_up: self.RUN,
                           a_down: self.RUN, s_down_ready: self.SKILL_SPIN},
                self.JUMP: {space_down: self.JUMP, z_down_with_cooldown: self.DASH, x_down: self.JUMP_ATTACK, a_down: self.JUMP},
                self.DASH: {space_down: self.JUMP},
                self.ATTACK1: {z_down_with_cooldown: self.DASH, space_down: self.JUMP},
                self.ATTACK2: {z_down_with_cooldown: self.DASH, space_down: self.JUMP},
                self.JUMP_ATTACK: {space_down: self.JUMP, z_down_with_cooldown: self.DASH},
                self.SKILL_SPIN: {}
            }
        )

    def get_bb_feet(self):
        return self.x - self.half_w, self.y - self.half_h, self.x + self.half_w, self.y - self.half_h + 5

    def get_bb_body(self):
        return self.x - self.half_w, self.y - self.half_h + 10, self.x + self.half_w, self.y + self.half_h

    def check_ground(self):
        self.on_ground = False

        self.half_w = (50 * SCALE) / 2
        self.half_h = (50 * SCALE) / 2

        my_feet = self.get_bb_feet()
        if not self.platforms:
            return

        for p in self.platforms:
            platform_bb = p.get_bb()
            left_a, bottom_a, right_a, top_a = my_feet
            left_b, bottom_b, right_b, top_b = platform_bb
            if left_a > right_b: continue
            if right_a < left_b: continue
            if top_a < bottom_b: continue
            if bottom_a > top_b: continue

            if self.vy <= 0:
                self.on_ground = True
                self.vy = 0
                self.y = platform_bb[3] + self.half_h
                return

    def check_wall_collision(self):
        my_body = self.get_bb_body()
        if not self.platforms:
            return

        for p in self.platforms:
            platform_bb = p.get_bb()

            if my_body[0] > platform_bb[2]: continue
            if my_body[2] < platform_bb[0]: continue
            if my_body[3] < platform_bb[1]: continue
            if my_body[1] > platform_bb[3]: continue

            if self.y < platform_bb[3] + self.half_h - 5:
                if self.x < p.x and self.dir > 0:
                    self.x = platform_bb[0] - self.half_w
                elif self.x > p.x and self.dir < 0:
                    self.x = platform_bb[2] + self.half_w

    def get_attack_bb(self):
        return self.get_bb()

    def check_attack_collision(self, hit_enemies):
        attack_bb = self.get_attack_bb()

        for o in game_world.all_objects():
            if o == self:
                continue
            if type(o).__name__ in ('EnemyKnight', 'EnemyTree', 'EnemyGreenTree', 'EnemyGiantTree') and id(o) not in hit_enemies:
                if collide(attack_bb, o.get_bb()):
                    o.take_damage(SKULL_ATTACK_DAMAGE, self.face_dir)
                    hit_enemies.append(id(o))

    def take_damage(self, damage_amount, attacker_pos_x=None):
        if self.invincible_timer > 0.0:
            return

        self.current_hp -= damage_amount

        if self.current_hp <= 0:
            game_framework.run(lobby_mode)

        self.invincible_timer = 1.5

        if self.current_hp <= 0:
            print("SKULL DIED!")
            game_framework.run(lobby_mode)


        self.invincible_timer = 1.5

    def update(self):
        # 쿨타임
        if self.skill_cooldown > 0:
            self.skill_cooldown -= game_framework.frame_time
            if self.skill_cooldown < 0:
                self.skill_cooldown = 0
        if self.skill_s_cooldown > 0:
            self.skill_s_cooldown -= game_framework.frame_time
            if self.skill_s_cooldown < 0:
                self.skill_s_cooldown = 0
        # 무적
        if self.invincible_timer > 0.0:
            self.invincible_timer -= game_framework.frame_time
        if self.y < 100:
            self.y += 50
        cur = self.state_machine.cur_state
        if cur not in (self.DASH,):
            self.vy -= GRAVITY_PPS * game_framework.frame_time
        self.y += self.vy * game_framework.frame_time
        if cur != self.DASH:
            self.check_ground()
        else:
            self.on_ground = False
        self.state_machine.update()

        # 맵 밖으로 나가지 않게 고정
        self.x = clamp(0 + self.half_w, self.x, self.world_w - self.half_w)

        cur_after_do = self.state_machine.cur_state
        if self.on_ground:
            if cur_after_do in (self.JUMP,):
                cur_after_do.exit(('LAND', None))
                self.recompute_dir()
                next_state = self.RUN if (self.left_pressed or self.right_pressed) else self.IDLE
                self.state_machine.cur_state = next_state
                next_state.enter(('LAND', None))
                self.jump_count = 0
            elif cur_after_do in (self.IDLE, self.RUN) and cur == self.JUMP_ATTACK:
                self.jump_count = 0
        else:
            if cur_after_do in (self.IDLE, self.RUN):
                cur_after_do.exit(('FALL', None))
                self.state_machine.cur_state = self.JUMP
                self.JUMP.enter(('FALL', None))

    def handle_event(self, event):
        from sdl2 import SDLK_UP

        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_RIGHT:
                self.right_pressed = True
            elif event.key == SDLK_LEFT:
                self.left_pressed = True
            elif event.key == SDLK_UP:
                self.up_pressed = True
            elif event.key == SDLK_DOWN:
                self.down_pressed = True
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT:
                self.right_pressed = False
            elif event.key == SDLK_LEFT:
                self.left_pressed = False
            elif event.key == SDLK_UP:
                self.up_pressed = True
            elif event.key == SDLK_DOWN:
                self.down_pressed = False

        event_tuple = ('INPUT', event)
        handled_by_state = False

        if hasattr(self.state_machine.cur_state, 'handle_event'):
            handled_by_state = self.state_machine.cur_state.handle_event(event_tuple)

        if not handled_by_state:
            self.state_machine.handle_state_event(event_tuple)

    def draw(self, camera_x, camera_y):
        if self.invincible_timer > 0.0 and self.state_machine.cur_state != self.DASH:
            if int(self.invincible_timer * 10) % 2 == 0:
                pass
            else:
                self.state_machine.draw(camera_x, camera_y)
        else:
            self.state_machine.draw(camera_x, camera_y)

        lx, by, rx, ty = self.get_attack_bb()
        #draw_rectangle(lx - camera_x, by - camera_y, rx - camera_x, ty - camera_y)


    def fire_ball(self):
        if self.skill_cooldown > 0:
            return
        ball = Ball(self.x, self.y, self.face_dir * 10, self.world_w)
        game_world.add_object(ball)

        self.skill_cooldown = 5.0

    def recompute_dir(self):
        r = 1 if self.right_pressed else 0
        l = 1 if self.left_pressed else 0
        self.dir = r - l
        if self.dir != 0:
            self.face_dir = 1 if self.dir > 0 else -1

    def get_bb(self):
        current_w, current_H = 50, 30
        half_w = (current_w * SCALE) / 2
        half_h = (current_H * SCALE) / 2
        return self.x - half_w, self.y - half_h- 30, self.x + half_w, self.y + half_h