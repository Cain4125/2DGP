from pico2d import load_image, draw_rectangle
import game_world
from ground import Ground
import camera
from enemy_knight import EnemyKnight
import game_framework
import battle_stage
from constants import SCALE

WORLD_WIDTH_PIXELS = 3000
WORLD_HEIGHT_PIXELS = 800

def collide(bb_a, bb_b):
    left_a, bottom_a, right_a, top_a = bb_a
    left_b, bottom_b, right_b, top_b = bb_b
    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False
    return True


class Portal:
    image = None

    def __init__(self, x, y):
        if Portal.image is None:
            Portal.image = load_image('portal.png')
        self.x, self.y = x, y
        self.w, self.h = 176, 128
        self.half_w = self.w * SCALE / 2
        self.half_h = self.h * SCALE / 2

    def draw(self, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        self.image.draw(screen_x, screen_y, self.w * SCALE, self.h * SCALE)
        draw_rectangle(self.x - self.half_w - camera_x, self.y - self.half_h - camera_y,
                       self.x + self.half_w - camera_x, self.y + self.half_h - camera_y)

    def update(self):
        pass

    def get_bb(self):
        return (self.x - self.half_w,
                self.y - self.half_h,
                self.x + self.half_w,
                self.y + self.half_h)

class StartMap:
    def __init__(self, skull):
        self.skull = skull

        # 1. 발판 뼈대
        self.ground = Ground(WORLD_WIDTH_PIXELS // 2, 30, WORLD_WIDTH_PIXELS, 60)
        self.platform1 = Ground(700, 150, 200, 40)
        self.platform2 = Ground(1050, 350, 100, 40)
        self.platform3 = Ground(1600, 350, 300, 40)
        self.platforms = [self.ground, self.platform1, self.platform2, self.platform3]

        self.knights = [EnemyKnight(1600, 200, self.skull, self.platforms),
                        #EnemyKnight(800, 210, self.skull, self.platforms)
                        ]

        portal_x = WORLD_WIDTH_PIXELS - 100
        portal_y = 60 + (128 * SCALE) / 2

        self.portal = Portal(portal_x, portal_y)


    def enter(self):
        game_world.clear()
        game_world.add_object(self.skull, 2)

        for p in self.platforms:
            game_world.add_object(p, 0)

        for e in self.knights:
            game_world.add_object(e, 1)


        self.skull.platforms = self.platforms

        self.skull.x, self.skull.y = 100, 135
        self.skull.vy = 0

        camera.camera.set_target_and_world(self.skull, WORLD_WIDTH_PIXELS, WORLD_HEIGHT_PIXELS)

    def exit(self):
        pass

    def update(self):
        if collide(self.skull.get_bb(), self.portal.get_bb()):
            # Skull의 right_pressed 플래그를 확인하여 오른쪽 키가 눌렸는지 체크
            if self.skull.right_pressed:
                # BattleStage로 모드 전환
                new_mode = battle_stage.BattleStage(self.skull)
                game_framework.change_mode(new_mode)
                return new_mode

        return None

    def handle_events(self, event):
        self.skull.handle_event(event)