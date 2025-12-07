from pico2d import load_image, draw_rectangle, load_font
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

# 텍스트
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

# 배경장식
class Decoration:
    def __init__(self, x, file_name, ground_y=60):
        self.image = load_image(file_name)
        self.x = x
        self.scale = SCALE/1.5

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
        self.w = WORLD_WIDTH_PIXELS
        self.h = WORLD_HEIGHT_PIXELS

    def draw(self, camera_x, camera_y):
        self.image.draw(self.w // 2 - camera_x, self.h // 2 - camera_y, self.w, self.h)

        self.image2.draw(self.w // 2 - camera_x, self.h // 2 - camera_y, self.w, self.h)

    def update(self):
        pass

    def get_bb(self):
        return 0, 0, 0, 0


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
        #draw_rectangle(self.x - self.half_w - camera_x, self.y - self.half_h - camera_y,
                     #  self.x + self.half_w - camera_x, self.y + self.half_h - camera_y)

    def update(self):
        pass



class StartMap:
    def __init__(self, skull):
        self.skull = skull

        self.ground = Ground(WORLD_WIDTH_PIXELS // 2, 30, WORLD_WIDTH_PIXELS, 60, is_main=True)
        self.platform1 = Ground(700, 150, 200, 40)
        self.platform2 = Ground(1050, 350, 100, 40)
        self.platform3 = Ground(1600, 350, 300, 40)
        self.platforms = [self.ground, self.platform1, self.platform2, self.platform3]

        self.knights = [EnemyKnight(1600, 200, self.skull, self.platforms)
                        ]
        self.tree = [EnemyGreenTree(1600, 100, self.skull, self.platforms),]
        self.trees = [
            Decoration(200, 'Tree02.png'),
            #Decoration(900, 'Tree01.png'),
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

            TutorialText(1200, 200, "Attack: X / Skill: A/S", size=25, color=(255, 50, 50)),

            TutorialText(2700,250,"Up arrow key", size = 25, color=(255, 255, 255)),

            TutorialText(1550, 420, "Down arrow key + SPACE (Drop Down)", size=25, color=(255, 255, 255))
        ]

        portal_x = WORLD_WIDTH_PIXELS - 220
        portal_y = 60 + (128 * SCALE) / 2

        self.portal = Portal(portal_x, portal_y)

        self.bg = FixedBackground()

    def enter(self):
        game_world.clear()

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