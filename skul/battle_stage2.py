from pico2d import load_image, load_music, load_wav
import game_world
from ground import Ground
from spikepit import SpikePit
import camera
import game_framework
from constants import SCALE

from enemy_knight import EnemyKnight
from enemy_greentree import EnemyGreenTree
from enemy_tree import EnemyTree

WORLD_WIDTH_PIXELS = 3000
WORLD_HEIGHT_PIXELS = 1500


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


class BattleStage2:
    def __init__(self, skull):
        self.skull = skull

        self.ground_left = Ground(500, 175, 1000, 350, is_main=True)
        self.ground_pit = Ground(1600, 50, 1200, 100, is_main=True)
        self.ground_right = Ground(2600, 175, 800, 350, is_main=True)

        self.spikes = []
        spike_spacing = 100
        spike_count = 11
        first_spike_center_x = 1100
        spike_y = 105

        for i in range(spike_count):
            spike_x = first_spike_center_x + (i * spike_spacing)
            self.spikes.append(SpikePit(spike_x, spike_y, self.skull))

        self.platforms = [self.ground_left, self.ground_pit, self.ground_right]

        self.long_sky_platform = Ground(1500, 900, 1000, 60)
        self.platforms.append(self.long_sky_platform)

        self.platforms.append(Ground(1600, 300, 250, 40))
        self.platforms.append(Ground(2200, 550, 200, 40))
        self.platforms.append(Ground(1900, 750, 200, 40))

        self.enemies = []

        self.enemies.append(EnemyKnight(700, 450, self.skull, self.platforms))
        self.enemies.append(EnemyKnight(900, 450, self.skull, self.platforms))

        self.enemies.append(EnemyTree(1600, 400, self.skull, self.platforms))

        self.enemies.append(EnemyKnight(2450, 450, self.skull, self.platforms))
        self.enemies.append(EnemyTree(2550, 450, self.skull, self.platforms))

        self.enemies.append(EnemyGreenTree(2200, 650, self.skull, self.platforms))
        self.enemies.append(EnemyGreenTree(1900, 850, self.skull, self.platforms))

        portal_x = self.long_sky_platform.x
        portal_y = self.long_sky_platform.y + 30 + (128 * SCALE) / 2
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

        for s in self.spikes:
            game_world.add_object(s, 1)

        game_world.add_object(self.portal, 0)

        self.skull.platforms = self.platforms

        self.skull.x, self.skull.y = 200, 500
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
            return 'battle_stage3'

        return None

    def handle_events(self, event):
        self.skull.handle_event(event)