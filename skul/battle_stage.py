import game_world
from ground import Ground
import camera
from enemy_knight import EnemyKnight

WORLD_WIDTH_PIXELS = 2000
WORLD_HEIGHT_PIXELS = 800


class BattleStage:
    def __init__(self, skull):
        self.skull = skull

        # 1. 발판 뼈대
        self.ground = Ground(WORLD_WIDTH_PIXELS // 2, 30, WORLD_WIDTH_PIXELS, 60)

        self.platforms = [self.ground]

        self.knights = [EnemyKnight(600, 150, self.skull, self.platforms),
                        #EnemyKnight(800, 210, self.skull, self.platforms)
                        ]



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
        # (나중에 여기에 포탈 충돌 검사)
        return None

    def handle_events(self, event):
        self.skull.handle_event(event)