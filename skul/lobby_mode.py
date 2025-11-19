from pico2d import *
import game_framework
import play_mode

def enter():
    global image
    image = load_image('Title.png')

def finish():
    global image
    del image

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            game_framework.change_mode(play_mode)

def update():
    pass

def draw():
    clear_canvas()
    image.draw(700, 400)
    update_canvas()

def pause():
    pass

def resume():
    pass