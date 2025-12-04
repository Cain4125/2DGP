from pico2d import *
import game_world
import camera

def collide(bb_a, bb_b):
    left_a, bottom_a, right_a, top_a = bb_a
    left_b, bottom_b, right_b, top_b = bb_b
    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False
    return True

# python
class Ball:
    image = None

    def __init__(self, x, y, velocity, world_w, scale=3, speed_scale=0.5, damage = 10):
        if Ball.image is None:
            Ball.image = load_image('Skul_Skill.png')
        self.x = x
        self.y = y
        self.velocity = velocity
        self.world_w = world_w
        self.scale = scale
        self.speed_scale = speed_scale
        self.draw_w = int(Ball.image.w * self.scale)
        self.draw_h = int(Ball.image.h * self.scale)
        self.damage = damage

    def get_bb(self):
        # 충돌 박스 크기
        half_w = self.draw_w / 2
        half_h = self.draw_h / 2
        return self.x - half_w, self.y - half_h, self.x + half_w, self.y + half_h

    def draw(self, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        self.image.draw(screen_x, screen_y, self.draw_w, self.draw_h)

        l, b, r, t = self.get_bb()
        draw_rectangle(l - camera_x, b - camera_y, r - camera_x, t - camera_y)

    def update(self):
        self.x += self.velocity * self.speed_scale
        if self.x < 0 - self.draw_w / 2 or self.x > self.world_w + self.draw_w / 2:
            game_world.remove_object(self)
        self.check_collision_with_enemies()

    def check_collision_with_enemies(self):
        for o in game_world.all_objects():
            if type(o).__name__ in ('EnemyKnight', 'EnemyTree'):
                if collide(self.get_bb(), o.get_bb()):
                    knockback_dir = 1 if self.velocity > 0 else -1
                    o.take_damage(self.damage, knockback_dir)
                    game_world.remove_object(self)
                    return
