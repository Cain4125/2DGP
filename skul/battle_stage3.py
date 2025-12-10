from pico2d import load_image, draw_rectangle, load_font
import game_world
from ground import Ground
from spikepit import SpikePit
import camera
import game_framework
from constants import SCALE
import random

from enemy_knight import EnemyKnight
from enemy_greentree import EnemyGreenTree
from enemy_tree import EnemyTree

WORLD_WIDTH_PIXELS = 2500
WORLD_HEIGHT_PIXELS = 1300


class FixedBackground:
    def __init__(self):
        self.image = load_image('sky2.png')
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


class Portal:
    image_close = None
    image_open = None

    def __init__(self, x, y):
        if Portal.image_close is None:
            Portal.image_close = load_image('Portal_closed.png')
        if Portal.image_open is None:
            Portal.image_open = load_image('Portal_opened.png')
        self.x, self.y = x, y
        self.w, self.h = 176, 128
        self.scale = SCALE

        self.active = False
        self.frame = 0
        self.f_frame = 0.0
        self.fps = 10.0
        self.frame_count = 7

    def update(self):
        if self.active:
            self.f_frame = (self.f_frame + self.fps * game_framework.frame_time) % self.frame_count
            self.frame = int(self.f_frame)

    def draw(self, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        width = self.w * self.scale
        height = self.h * self.scale

        if self.active:
            sx = self.frame * self.w
            self.image_open.clip_draw(sx, 0, self.w, self.h, screen_x, screen_y, width, height)
        else:
            self.image_close.draw(screen_x, screen_y, width, height)

    def activate(self):
        self.active = True


class BattleStage3:
    def __init__(self, skull):
        self.skull = skull

        self.ground_left = Ground(400, 200, 800, 400, is_main=True)
        self.ground_pit = Ground(1250, 125, 900, 250, is_main=True)
        self.ground_right = Ground(2100, 200, 800, 400, is_main=True)

        self.platforms = [self.ground_left, self.ground_pit, self.ground_right]

        self.platforms.append(Ground(1250, 900, 1000, 60))
        self.platforms.append(Ground(600, 600, 250, 40))
        self.platforms.append(Ground(1900, 600, 250, 40))
        self.platforms.append(Ground(600, 750, 250, 40))
        self.platforms.append(Ground(1900, 750, 250, 40))

        self.enemies = []

        self.enemies.append(EnemyGreenTree(600, 800, self.skull, self.platforms))
        self.enemies.append(EnemyGreenTree(1900, 800, self.skull, self.platforms))

        self.enemies.append(EnemyKnight(200, 600, self.skull, self.platforms))
        self.enemies.append(EnemyKnight(400, 600, self.skull, self.platforms))
        self.enemies.append(EnemyTree(600, 600, self.skull, self.platforms))
        self.enemies.append(EnemyTree(750, 600, self.skull, self.platforms))

        self.enemies.append(EnemyKnight(1800, 600, self.skull, self.platforms))
        self.enemies.append(EnemyKnight(2000, 600, self.skull, self.platforms))
        self.enemies.append(EnemyTree(2200, 600, self.skull, self.platforms))
        self.enemies.append(EnemyTree(2400, 600, self.skull, self.platforms))

        start_x = 850
        gap = 130
        spawn_y = 1100

        self.enemies.append(EnemyKnight(start_x, spawn_y, self.skull, self.platforms))
        self.enemies.append(EnemyKnight(start_x + gap, spawn_y, self.skull, self.platforms))

        self.enemies.append(EnemyGreenTree(start_x + gap * 2, spawn_y, self.skull, self.platforms))
        self.enemies.append(EnemyGreenTree(start_x + gap * 3, spawn_y, self.skull, self.platforms))

        self.enemies.append(EnemyTree(start_x + gap * 4, spawn_y, self.skull, self.platforms))
        self.enemies.append(EnemyTree(start_x + gap * 5, spawn_y, self.skull, self.platforms))

        portal_x = 1250
        portal_y = 250 + (128 * SCALE) / 2
        self.portal = Portal(portal_x, portal_y)

        self.bg = FixedBackground()

    def enter(self):
        game_world.clear()

        self.skull.world_w = WORLD_WIDTH_PIXELS

        game_world.add_object(self.bg, 0)

        for e in self.enemies:
            game_world.add_object(e, 1)

        game_world.add_object(self.skull, 2)

        for p in self.platforms:
            game_world.add_object(p, 0)

        game_world.add_object(self.portal, 0)

        self.skull.platforms = self.platforms

        self.skull.x, self.skull.y = 1250, 450
        self.skull.vy = 0

        camera.camera.set_target_and_world(self.skull, WORLD_WIDTH_PIXELS, WORLD_HEIGHT_PIXELS)

    def exit(self):
        pass

    def update(self):
        all_enemies_dead = True
        for e in self.enemies:
            if e.alive:
                all_enemies_dead = False
                break

        if all_enemies_dead:
            self.portal.activate()

        portal_proximity_x = abs(self.skull.x - self.portal.x) < 50
        is_up_pressed = self.skull.up_pressed

        if portal_proximity_x and is_up_pressed and self.portal.active:
            return 'boss_map'

        return None

    def handle_events(self, event):
        self.skull.handle_event(event)