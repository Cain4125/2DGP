import game_world
from ground import Ground


class BattleStage:
    def __init__(self, skull):
        self.skull = skull
        self.ground = Ground(700, 30, 1400, 60)
        self.platforms = [self.ground]
        print("BattleStage 생성됨")

    def enter(self):
        game_world.clear()
        game_world.add_object(self.skull, 1)
        for p in self.platforms:
            game_world.add_object(p, 0)

        self.skull.platforms = self.platforms
        self.skull.x, self.skull.y = 100, 135
        self.skull.vy = 0

    def exit(self):
        pass

    def update(self):
        return None

    def handle_events(self, event):
        self.skull.handle_event(event)