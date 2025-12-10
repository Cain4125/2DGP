from pico2d import load_image, draw_rectangle, load_font, load_music
import game_world
from ground import Ground
import camera
import game_framework
from constants import SCALE
import random

from boss import EnemyGiantTree
from enemy_knight import EnemyKnight
from enemy_tree import EnemyTree
from enemy_greentree import EnemyGreenTree

WORLD_WIDTH_PIXELS = 1500
WORLD_HEIGHT_PIXELS = 800


class FixedBackground:
    def __init__(self):
        self.image = load_image('sky.png')
        self.image2 = load_image('mountain.png')
        self.image3 = load_image('trees.png')
        self.w = WORLD_WIDTH_PIXELS
        self.h = WORLD_HEIGHT_PIXELS

    def draw(self, camera_x, camera_y):
        self.image.draw(self.w // 2 - camera_x, self.h // 2 - camera_y, self.w, self.h)
        self.image2.draw(self.w // 2 - camera_x, self.h // 2.5 - camera_y, self.w, self.h)
        self.image3.draw(self.w // 2 - camera_x, self.h // 6 - camera_y, self.w, self.h)

    def update(self):
        pass

    def get_bb(self):
        return 0, 0, 0, 0


class BossStage:
    def __init__(self, skull):
        self.skull = skull
        self.ground = Ground(WORLD_WIDTH_PIXELS // 2, 30, WORLD_WIDTH_PIXELS, 60, is_main=True)

        self.platform_L1 = Ground(200, 180, 250, 40)
        self.platform_L2 = Ground(350, 320, 200, 40)

        self.platform_R2 = Ground(1050, 320, 200, 40)
        self.platform_R1 = Ground(1400, 180, 250, 40)

        self.platforms = [
            self.ground,
            self.platform_L1, self.platform_L2,
            self.platform_R2, self.platform_R1
        ]

        self.boss = EnemyGiantTree(750, 250, self.skull)

        self.bg = FixedBackground()
        self.spawn_timer = 0.0

        self.bgm = load_music('boss.mp3')
        self.bgm.set_volume(64)

    def spawn_wave(self):
        for target_platform in [self.platform_L2, self.platform_R2]:
            gt_x = target_platform.x
            gt_y = target_platform.y + 100
            green_tree = EnemyGreenTree(gt_x, gt_y, self.skull, self.platforms)
            game_world.add_object(green_tree, 1)

        k_x = random.randint(100, 1400)
        knight = EnemyKnight(k_x, 300, self.skull, self.platforms)
        game_world.add_object(knight, 1)

        t_x = random.randint(100, 1400)
        tree = EnemyTree(t_x, 300, self.skull, self.platforms)
        game_world.add_object(tree, 1)

    def enter(self):
        game_world.clear()
        self.skull.world_w = WORLD_WIDTH_PIXELS
        game_world.add_object(self.bg, 0)

        game_world.add_object(self.boss, 1)

        game_world.add_object(self.skull, 2)

        for p in self.platforms:
            game_world.add_object(p, 0)

        self.skull.platforms = self.platforms

        self.skull.x, self.skull.y = 100, 135
        self.skull.vy = 0

        camera.camera.set_target_and_world(self.skull, WORLD_WIDTH_PIXELS, WORLD_HEIGHT_PIXELS)

        self.bgm.repeat_play()

        self.spawn_wave()
        self.spawn_timer = 0.0

    def exit(self):
        self.bgm.stop()

    def update(self):
        self.spawn_timer += game_framework.frame_time
        if self.spawn_timer >= 15.0:
            self.spawn_wave()
            self.spawn_timer = 0.0

        return None

    def handle_events(self, event):
        self.skull.handle_event(event)