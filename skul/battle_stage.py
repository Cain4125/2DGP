from pico2d import load_image, load_music, load_wav
import game_world
from ground import Ground
import camera
import game_framework
from constants import SCALE

from enemy_knight import EnemyKnight
from enemy_tree import EnemyTree

WORLD_WIDTH_PIXELS = 4000
WORLD_HEIGHT_PIXELS = 1200


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


class BattleStage:
    def __init__(self, skull):
        self.skull = skull

        self.ground_left = Ground(700, 150, 1400, 300, is_main=True)
        self.ground_pit = Ground(2000, 50, 1200, 100, is_main=True)
        self.ground_right = Ground(3300, 150, 1400, 300, is_main=True)

        self.spawn_platform = Ground(125, 650, 250, 40)
        self.mid_platform = Ground(850, 450, 200, 40)

        self.platforms = [
            self.ground_left, self.ground_pit, self.ground_right,
            self.spawn_platform, self.mid_platform
        ]

        self.enemies = []

        for i in range(10):
            x = 400 + (i * 100)
            y = 500
            self.enemies.append(EnemyKnight(x, y, self.skull, self.platforms))

        for i in range(5):
            x = 1600 + (i * 200)
            y = 300
            self.enemies.append(EnemyKnight(x, y, self.skull, self.platforms))

        self.enemies.append(EnemyTree(3300, 550, self.skull, self.platforms))

        portal_x = 3500
        portal_y = 300 + (128 * SCALE) / 2
        self.portal = Portal(portal_x, portal_y)

        self.bg = FixedBackground()

        self.bgm = load_music('playmode.mp3')
        self.bgm.set_volume(64)

        self.portal_sound = load_wav('door_open.wav')
        self.portal_sound.set_volume(32)

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

        self.skull.x, self.skull.y = 230, 750
        self.skull.vy = 0

        camera.camera.set_target_and_world(self.skull, WORLD_WIDTH_PIXELS, WORLD_HEIGHT_PIXELS)

        self.bgm.repeat_play()

    def exit(self):
        self.bgm.stop()

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
            self.portal_sound.play()
            return 'battle_stage2'

        return None

    def handle_events(self, event):
        self.skull.handle_event(event)