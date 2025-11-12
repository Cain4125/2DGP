from pico2d import *
from skull import Skull
import game_world
import game_framework
import camera
from start_map import StartMap
from battle_stage import BattleStage

skull_player = None
stages = {}
current_stage = None
WORLD_WIDTH_PIXELS = 5000
WORLD_HEIGHT_PIXELS = 800

def init():
    global skull_player, stages, current_stage
    skull_player = Skull(platforms=[], world_w=WORLD_WIDTH_PIXELS)
    camera.camera.set_target_and_world(skull_player, WORLD_WIDTH_PIXELS, WORLD_HEIGHT_PIXELS)
    stages = {
        'start_map': StartMap(skull_player),
        'battle_stage': BattleStage(skull_player),
    }
    current_stage = stages['start_map']
    current_stage.enter()

def finish():
    global skull_player
    game_world.clear()
    del skull_player
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

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def pause():
    pass

def resume():
    pass