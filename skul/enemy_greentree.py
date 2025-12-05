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


class GreenTreeIdle:
    image = None

    def __init__(self, tree):
        self.tree = tree
        if GreenTreeIdle.image is None:
            GreenTreeIdle.image = load_image('greentree_idle.png')

        # [수정] 300 / 5 = 60
        self.cell_w = 60
        self.cell_h = 66

    def enter(self, e):
        self.tree.f_frame = 0.0
        self.tree.frame = 0
        self.tree.dir = 0

        # 상태 변경 시 스프라이트 크기 정보 업데이트 (드로잉 보정용)
        self.tree.sprite_w = self.cell_w
        self.tree.sprite_h = self.cell_h

    def exit(self):
        pass

    def do(self):
        self.tree.f_frame = (self.tree.f_frame + ENEMY_IDLE_FPS * game_framework.frame_time) % 5
        self.tree.frame = int(self.tree.f_frame)

        if not self.tree.target:
            return

        dist_x = self.tree.target.x - self.tree.x
        dist_y = abs(self.tree.target.y - self.tree.y)

        if dist_x > 0:
            self.tree.face_dir = 1
        else:
            self.tree.face_dir = -1

        detect_range_x = DETECT_RANGE * 2.5
        detect_range_y = 350

        if abs(dist_x) < detect_range_x and dist_y <= detect_range_y and self.tree.attack_cooldown <= 0:
            self.tree.change_state(self.tree.ATTACK, None)

    def draw(self, cx, cy):
        sx = self.cell_w * self.tree.frame
        x = self.tree.x - cx
        y_offset = (self.cell_h / 2) - (self.tree.hit_h / 2)
        y = (self.tree.y - cy) + (y_offset * SCALE)
        w = self.tree.sprite_w * SCALE
        h = self.tree.sprite_h * SCALE

        if self.tree.face_dir == 1:
            GreenTreeIdle.image.clip_draw(sx, 0, self.cell_w, self.cell_h, x, y, w, h)
        else:
            GreenTreeIdle.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'h', x, y, w, h)


class GreenTreeAttack:
    image = None

    def __init__(self, tree):
        self.tree = tree
        if GreenTreeAttack.image is None:
            GreenTreeAttack.image = load_image('greentree_attack.png')

        # [수정] 656 / 8 = 82
        self.cell_w = 82
        self.cell_h = 68

        self.played_once = False
        self.hold = 0.0

    def enter(self, e):
        self.tree.f_frame = 0.0
        self.tree.frame = 0
        self.played_once = False
        self.tree.dir = self.tree.face_dir
        self.hold = 0.8

        # 상태 변경 시 스프라이트 크기 정보 업데이트
        self.tree.sprite_w = self.cell_w
        self.tree.sprite_h = self.cell_h

    def exit(self):
        pass

    def do(self):
        if not self.played_once:
            self.tree.f_frame += ENEMY_ATTACK_FPS * game_framework.frame_time

            if self.tree.f_frame >= 8.0:
                self.played_once = True
                self.tree.frame = 7
            else:
                self.tree.frame = int(self.tree.f_frame)
        else:
            self.hold -= game_framework.frame_time
            if self.hold <= 0:
                self.tree.attack_cooldown = 4.0
                self.tree.change_state(self.tree.IDLE, None)

    def draw(self, cx, cy):
        sx = self.cell_w * self.tree.frame
        x = self.tree.x - cx
        y_offset = (self.cell_h / 2) - (self.tree.hit_h / 2)
        y = (self.tree.y - cy) + (y_offset * SCALE)
        w = self.tree.sprite_w * SCALE
        h = self.tree.sprite_h * SCALE
        if self.tree.face_dir == 1:
            GreenTreeAttack.image.clip_draw(sx, 0, self.cell_w, self.cell_h, x, y, w, h)
        else:
            GreenTreeAttack.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'h', x, y, w, h)


class GreenTreeHit:
    image = None

    def __init__(self, tree):
        self.tree = tree
        if GreenTreeHit.image is None:
            GreenTreeHit.image = load_image('greentree_hit.png')

        # [수정] 124 / 2 = 62
        self.cell_w = 62
        self.cell_h = 66

        self.anim_duration = 0.0
        self.state_duration = 0.0

    def enter(self, attacker_face_dir):
        self.tree.f_frame = 0.0
        self.tree.frame = 0
        if attacker_face_dir:
            self.tree.knockback_dir = attacker_face_dir
        else:
            self.tree.knockback_dir = 0

        self.anim_duration = 0.2
        self.state_duration = 0.5

        # 상태 변경 시 스프라이트 크기 정보 업데이트
        self.tree.sprite_w = self.cell_w
        self.tree.sprite_h = self.cell_h

    def exit(self):
        pass

    def do(self):
        self.state_duration -= game_framework.frame_time

        if self.state_duration <= 0:
            self.tree.change_state(self.tree.IDLE, None)
            return

        if self.anim_duration > 0:
            self.anim_duration -= game_framework.frame_time
            self.tree.f_frame = (self.tree.f_frame + 10 * game_framework.frame_time) % 2
            self.tree.frame = int(self.tree.f_frame)
            self.tree.x += self.tree.knockback_dir * KNOCKBACK_SPEED_PPS * game_framework.frame_time
        else:
            self.tree.frame = 1

    def draw(self, cx, cy):
        sx = self.cell_w * self.tree.frame
        x = self.tree.x - cx
        y_offset = (self.cell_h / 2) - (self.tree.hit_h / 2)
        y = (self.tree.y - cy) + (y_offset * SCALE)
        w = self.tree.sprite_w * SCALE
        h = self.tree.sprite_h * SCALE
        if self.tree.face_dir == 1:
            GreenTreeHit.image.clip_draw(sx, 0, self.cell_w, self.cell_h, x, y, w, h)
        else:
            GreenTreeHit.image.clip_composite_draw(sx, 0, self.cell_w, self.cell_h, 0, 'h', x, y, w, h)


class EnemyGreenTree:
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

        # 초기 상태는 IDLE이므로 IDLE 크기로 설정
        self.sprite_w = 60
        self.sprite_h = 66

        self.hit_w = 50
        self.hit_h = 50
        self.half_hit_w = (self.hit_w * SCALE) / 2
        self.half_hit_h = (self.hit_h * SCALE) / 2

        self.target = target
        self.platforms = platforms
        self.attack_cooldown = 2.0
        self.knockback_dir = 0

        self.max_hp = ENEMY_TREE_MAX_HP
        self.current_hp = self.max_hp
        self.alive = True

        self.IDLE = GreenTreeIdle(self)
        self.ATTACK = GreenTreeAttack(self)
        self.HIT = GreenTreeHit(self)
        self.RUN = None
        self.JUMP = self.DUMMY_JUMP()

        self.cur_state = self.IDLE
        self.cur_state.enter(None)

    def change_state(self, new, e):
        if self.cur_state == new and self.cur_state != self.HIT:
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

    def take_damage(self, damage_amount, attacker_face_dir):
        if not self.alive:
            return

        self.current_hp -= damage_amount
        print(f"GREEN TREE HIT! HP: {self.current_hp}")

        if self.current_hp <= 0:
            self.alive = False
            y_offset_to_sink = (self.hit_h * SCALE / 2) - (33 * SCALE / 2)
            dead_body = DeadGreenTree(
                self.x,
                self.y - y_offset_to_sink,
                'tree_dead.png',
                76, 33, 6.0
            )
            game_world.add_object(dead_body, 0)

        if self.alive:
            self.change_state(self.HIT, attacker_face_dir)

    def update(self):
        self.attack_cooldown -= game_framework.frame_time
        if self.cur_state != self.HIT:
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
        if not self.alive: return
        self.cur_state.draw(cx, cy)


class DeadGreenTree:
    def __init__(self, x, y, image_name, sprite_w, sprite_h, duration=3.0):
        self.image = load_image(image_name)
        self.x, self.y = x, y
        self.sprite_w = sprite_w
        self.sprite_h = sprite_h
        self.scale = SCALE
        self.timer = duration

    def update(self):
        self.timer -= game_framework.frame_time
        if self.timer <= 0:
            game_world.remove_object(self)

    def draw(self, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        self.image.draw(screen_x, screen_y, self.sprite_w * self.scale, self.sprite_h * self.scale)

    def get_bb(self):
        return 0, 0, 0, 0