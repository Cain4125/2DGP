from pico2d import load_image, get_events, clear_canvas, update_canvas, load_font
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE, SDL_MOUSEBUTTONDOWN
import game_framework
import play_mode


class EndingMode:
    image = None
    font_title = None
    font_button = None

    def __init__(self, result):
        self.result = result

        if EndingMode.image is None:
            EndingMode.image = load_image('ending.png')

        if EndingMode.font_title is None:
            EndingMode.font_title = load_font('Cafe24PROUP.ttf', 100)
        if EndingMode.font_button is None:
            EndingMode.font_button = load_font('Cafe24PROUP.ttf', 40)

        self.canvas_w = 1400
        self.canvas_h = 800

        center_x = self.canvas_w // 2
        base_y = 200

        self.btn_restart_rect = (center_x - 200, base_y - 30, center_x - 50, base_y + 30)
        self.btn_exit_rect = (center_x + 50, base_y - 30, center_x + 200, base_y + 30)

    def enter(self):
        pass

    def finish(self):
        pass

    def update(self):
        pass

    def draw(self):

        self.image.draw(self.canvas_w // 2, self.canvas_h // 2, 1000, 700)

        text = "CLEAR!" if self.result == 'CLEAR' else "FAIL"
        text_x = self.canvas_w // 2 - (150 if self.result == 'CLEAR' else 100)
        text_y = self.canvas_h // 2 + 50

        self.font_title.draw(text_x - 3, text_y, text, (0, 0, 0))
        self.font_title.draw(text_x + 3, text_y, text, (0, 0, 0))
        self.font_title.draw(text_x, text_y - 3, text, (0, 0, 0))
        self.font_title.draw(text_x, text_y + 3, text, (0, 0, 0))
        self.font_title.draw(text_x, text_y, text, (255, 255, 255))

        r_x, r_y = self.btn_restart_rect[0], (self.btn_restart_rect[1] + self.btn_restart_rect[3]) // 2
        self.font_button.draw(r_x, r_y, "RESTART", (0, 0, 0))
        self.font_button.draw(r_x + 2, r_y + 2, "RESTART", (255, 255, 255))

        e_x, e_y = self.btn_exit_rect[0], (self.btn_exit_rect[1] + self.btn_exit_rect[3]) // 2
        self.font_button.draw(e_x + 30, e_y, "EXIT", (0, 0, 0))
        self.font_button.draw(e_x + 32, e_y + 2, "EXIT", (255, 255, 255))

        update_canvas()

    def handle_events(self, frame_time=0.0):
        events = get_events()
        for event in events:
            if event.type == SDL_QUIT:
                game_framework.quit()
            elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.type == SDL_MOUSEBUTTONDOWN:
                x, y = event.x, self.canvas_h - 1 - event.y

                if (self.btn_restart_rect[0] <= x <= self.btn_restart_rect[2] and
                        self.btn_restart_rect[1] <= y <= self.btn_restart_rect[3]):
                    game_framework.change_mode(play_mode)

                elif (self.btn_exit_rect[0] <= x <= self.btn_exit_rect[2] and
                      self.btn_exit_rect[1] <= y <= self.btn_exit_rect[3]):
                    game_framework.quit()