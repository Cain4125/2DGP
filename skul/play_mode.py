from pico2d import *
from skull import Skull
import game_world
import game_framework
import camera
from start_map import StartMap
from battle_stage import BattleStage
from boss_map import BossStage
from battle_stage2 import BattleStage2
from battle_stage3 import BattleStage3
from ui import UI

skull_player = None
stages = {}
current_stage = None
ui = None
WORLD_WIDTH_PIXELS = 5000
WORLD_HEIGHT_PIXELS = 800


def enter():
    global skull_player, stages, current_stage, ui
    skull_player = Skull(platforms=[], world_w=WORLD_WIDTH_PIXELS)
    camera.camera.set_target_and_world(skull_player, WORLD_WIDTH_PIXELS, WORLD_HEIGHT_PIXELS)

    stages = {
        'start_map': StartMap(skull_player),
        'battle_stage': BattleStage(skull_player),
        'boss_map': BossStage(skull_player),
        'battle_stage2': BattleStage2(skull_player),
        'battle_stage3': BattleStage3(skull_player)
    }

    current_stage = stages['start_map']
    current_stage.enter()

    ui = UI(skull_player)


def finish():
    global skull_player, ui, stages
    game_world.clear()
    skull_player = None
    ui = None
    stages.clear()
    camera.camera.init()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            current_stage.handle_events(event)


def update():
    global current_stage
    transition_to = current_stage.update()
    if transition_to:
        current_stage.exit()
        current_stage = stages[transition_to]
        current_stage.enter()

    game_world.update()
    camera.camera.update()

    if ui:
        ui.update()


def draw():
    clear_canvas()
    game_world.render()
    if ui:
        ui.draw(camera.camera.x, camera.camera.y)
    update_canvas()


def pause():
    pass


def resume():
    pass