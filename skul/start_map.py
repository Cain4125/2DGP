# start_map.py
import game_world
from ground import Ground
import camera
from enemy_knight import EnemyKnight  # <--- [신규] 기사 뼈대 임포트

WORLD_WIDTH_PIXELS = 3000
WORLD_HEIGHT_PIXELS = 800


class StartMap:
    def __init__(self, skull):
        self.skull = skull

        # 1. 발판 뼈대
        self.ground = Ground(WORLD_WIDTH_PIXELS // 2, 30, WORLD_WIDTH_PIXELS, 60)
        self.platform1 = Ground(400, 200, 200, 40)
        self.platform2 = Ground(1000, 300, 300, 40)
        self.platform3 = Ground(2000, 250, 500, 40)
        self.platforms = [self.ground, self.platform1, self.platform2, self.platform3]

        # 2. [신규] 적 뼈대
        # (스컬(target)과 발판 목록(platforms)을 뼈대로 넘겨줌)
        self.knight = EnemyKnight(1500, 210, self.skull, self.platforms)  # 800, 135 위치에 스폰

    def enter(self):
        game_world.clear()
        game_world.add_object(self.skull, 1)

        for p in self.platforms:
            game_world.add_object(p, 0)

        game_world.add_object(self.knight, 1)  # <--- [신규] 기사도 월드에 추가

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