from pico2d import load_image, draw_rectangle
import game_world
from ground import Ground
import camera
from enemy_knight import EnemyKnight
from enemy_tree import EnemyTree

WORLD_WIDTH_PIXELS = 2000
WORLD_HEIGHT_PIXELS = 800

class FixedBackground:
    def __init__(self):
        self.image = load_image('sky.png')
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

class BattleStage:
    def __init__(self, skull):
        self.skull = skull

        self.ground = Ground(WORLD_WIDTH_PIXELS // 2, 30, WORLD_WIDTH_PIXELS, 60, is_main=True)

        self.platforms = [self.ground]

        self.knights = [EnemyKnight(600, 100, self.skull, self.platforms),
                        EnemyKnight(1200, 100, self.skull, self.platforms)
                        ]

        self.trees = [EnemyTree(900, 90, self.skull, self.platforms),
                      EnemyTree(1500, 90, self.skull, self.platforms),]

        self.bg = FixedBackground()

    def enter(self):
        game_world.clear()
        game_world.add_object(self.bg, 0)
        game_world.add_object(self.skull, 2)

        for p in self.platforms:
            game_world.add_object(p, 0)

        for e in self.knights:
            game_world.add_object(e, 1)

        for t in self.trees:
            game_world.add_object(t, 1)


        self.skull.platforms = self.platforms

        self.skull.x, self.skull.y = 100, 135
        self.skull.vy = 0

        camera.camera.set_target_and_world(self.skull, WORLD_WIDTH_PIXELS, WORLD_HEIGHT_PIXELS)

    def exit(self):
        pass

    def update(self):
        # (나중에 여기에 포탈 충돌 검사)
        return None

    def handle_events(self, event):
        self.skull.handle_event(event)