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


class Portal:
    image = None

    def __init__(self, x, y):
        if Portal.image is None:
            Portal.image = load_image('portal.png')
        self.x, self.y = x, y
        self.w, self.h = 176, 128
        self.half_w = self.w * SCALE / 2.5
        self.half_h = self.h * SCALE / 2.5

    def draw(self, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        self.image.draw(screen_x, screen_y, self.w * SCALE, self.h * SCALE)
        draw_rectangle(self.x - self.half_w - camera_x, self.y - self.half_h - camera_y,
                       self.x + self.half_w - camera_x, self.y + self.half_h - camera_y)

    def update(self):
        pass



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

        portal_x = WORLD_WIDTH_PIXELS - 220
        portal_y = 60 + (128 * SCALE) / 2

        self.portal = Portal(portal_x, portal_y)


    def enter(self):
        game_world.clear()
        game_world.add_object(self.skull, 2)

        for p in self.platforms:
            game_world.add_object(p, 0)
        game_world.add_object(self.portal, 0)
        for e in self.knights:
            game_world.add_object(e, 1)


        self.skull.platforms = self.platforms

        self.skull.x, self.skull.y = 100, 135
        self.skull.vy = 0

        camera.camera.set_target_and_world(self.skull, WORLD_WIDTH_PIXELS, WORLD_HEIGHT_PIXELS)

    def exit(self):
        pass

    def update(self):
        portal_proximity_x = abs(self.skull.x - self.portal.x) < 50

        is_up_pressed = self.skull.up_pressed

        if portal_proximity_x and is_up_pressed:
            return 'battle_stage'

        return None

    def handle_events(self, event):
        self.skull.handle_event(event)