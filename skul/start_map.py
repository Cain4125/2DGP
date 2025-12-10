from pico2d import load_image, draw_rectangle, load_font, load_music, load_wav
import game_world
from ground import Ground
import camera
from enemy_knight import EnemyKnight
from enemy_greentree import EnemyGreenTree
import game_framework
import battle_stage
from constants import SCALE
from spikepit import SpikePit

WORLD_WIDTH_PIXELS = 3000
WORLD_HEIGHT_PIXELS = 800


class TutorialText:
    def __init__(self, x, y, text, size=20, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        try:
            self.font = load_font('Cafe24PROUP.ttf', size)
        except:
            print("폰트 파일을 찾을 수 없습니다.")

    def draw(self, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        outline_color = (0, 0, 0)
        self.font.draw(screen_x - 2, screen_y, self.text, outline_color)
        self.font.draw(screen_x + 2, screen_y, self.text, outline_color)
        self.font.draw(screen_x, screen_y - 2, self.text, outline_color)
        self.font.draw(screen_x, screen_y + 2, self.text, outline_color)

        self.font.draw(screen_x, screen_y, self.text, self.color)

    def update(self):
        pass

    def get_bb(self):
        return 0, 0, 0, 0


class Decoration:
    def __init__(self, x, file_name, ground_y=60):
        self.image = load_image(file_name)
        self.x = x
        self.scale = SCALE / 1.5

        self.w = self.image.w * self.scale
        self.h = self.image.h * self.scale

        self.y = ground_y + (self.h / 2) - 10

    def draw(self, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        self.image.draw(screen_x, screen_y, self.w, self.h)

    def update(self):
        pass

    def get_bb(self):
        return 0, 0, 0, 0


class FixedBackground:
    def __init__(self):
        self.image = load_image('sky2.png')
        self.image2 = load_image('mountain.png')
        self.image3 = load_image('trees.png')
        self.w = WORLD_WIDTH_PIXELS
        self.h = WORLD_HEIGHT_PIXELS

    def draw(self, camera_x, camera_y):
        self.image.draw(self.w // 2 - camera_x, self.h // 2 - camera_y, self.w, self.h)

        self.image2.draw(self.w // 2 - camera_x, self.h // 2 - camera_y, self.w, self.h)

        self.image3.draw(self.w // 2 - camera_x, self.h // 2 - camera_y, self.w, self.h)

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


class StartMap:
    def __init__(self, skull):
        self.skull = skull

        self.ground = Ground(WORLD_WIDTH_PIXELS // 2, 30, WORLD_WIDTH_PIXELS, 60, is_main=True)
        self.platform1 = Ground(700, 150, 200, 40)
        self.platform2 = Ground(1050, 350, 100, 40)
        self.platform3 = Ground(1600, 350, 300, 40)
        self.platforms = [self.ground, self.platform1, self.platform2, self.platform3]

        self.knights = [EnemyKnight(1600, 250, self.skull, self.platforms)]
        self.trees = [
            Decoration(200, 'Tree02.png'),
            Decoration(1800, 'Tree03.png'),
            Decoration(2600, 'Tree04.png')
        ]

        self.spikes = [
            SpikePit(1050, 75, self.skull)
        ]

        self.tutorial_texts = [
            TutorialText(550, 220, "SPACE (Jump)", size=25, color=(255, 255, 255)),
            TutorialText(850, 450, "SPACE x 2 (Double Jump)", size=25, color=(255, 255, 255)),
            TutorialText(1300, 500, "SPACE + Z (Dash)", size=25, color=(255, 255, 255)),
            TutorialText(1200, 200, "Attack: X / Skill: A,S", size=25, color=(255, 50, 50)),
            TutorialText(2700, 250, "Up arrow key", size=25, color=(255, 255, 255)),
            TutorialText(1550, 420, "Down arrow key + SPACE (Drop Down)", size=25, color=(255, 255, 255))
        ]

        portal_x = WORLD_WIDTH_PIXELS - 220
        portal_y = 60 + (128 * SCALE) / 2

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

        for tree in self.trees:
            game_world.add_object(tree, 0)

        game_world.add_object(self.skull, 2)

        for p in self.platforms:
            game_world.add_object(p, 0)
        game_world.add_object(self.portal, 0)
        for e in self.knights:
            game_world.add_object(e, 1)
        for z in self.spikes:
            game_world.add_object(z, 1)
        for text in self.tutorial_texts:
            game_world.add_object(text, 1)

        self.skull.platforms = self.platforms

        self.skull.x, self.skull.y = 100, 135
        self.skull.vy = 0

        camera.camera.set_target_and_world(self.skull, WORLD_WIDTH_PIXELS, WORLD_HEIGHT_PIXELS)

        self.bgm.repeat_play()

    def exit(self):
        self.bgm.stop()

    def update(self):
        all_enemies_dead = True
        for e in self.knights:
            if e.alive:
                all_enemies_dead = False
                break

        if all_enemies_dead:
            self.portal.activate()

        portal_proximity_x = abs(self.skull.x - self.portal.x) < 50
        is_up_pressed = self.skull.up_pressed

        if portal_proximity_x and is_up_pressed and self.portal.active:
            self.portal_sound.play()
            return 'battle_stage'

        return None

    def handle_events(self, event):
        self.skull.handle_event(event)