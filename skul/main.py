from pico2d import *
import game_framework
import lobby_mode
import play_mode

open_canvas(1400,800)
game_framework.run(play_mode)
close_canvas()