from pico2d import load_image, draw_rectangle


class Ground:
    image = None

    def __init__(self, x, y, w, h):
        if Ground.image is None:
            Ground.image = load_image('Grass_tile.png')
        self.tile_w = 32
        self.tile_h = 32
        self.x = x
        self.y = y
        self.half_w = w / 2
        self.half_h = h / 2

    def draw(self, camera_x, camera_y):
        l_phys, b_phys, r_phys, t_phys = self.get_bb()
        #draw_rectangle(l_phys - camera_x, b_phys - camera_y, r_phys - camera_x, t_phys - camera_y)
        visual_offset_y = 5
        draw_y_center = (self.y + self.half_h) - (self.tile_h / 2) + visual_offset_y
        current_x_center = (self.x - self.half_w) + (self.tile_w / 2)
        right_edge = self.x + self.half_w
        while current_x_center < right_edge + self.tile_w:
            screen_x = current_x_center - camera_x
            screen_y = draw_y_center - camera_y
            self.image.draw(screen_x, screen_y)
            current_x_center += self.tile_w

    def update(self):
        pass

    def get_bb(self):
        return (self.x - self.half_w, self.y - self.half_h,
                self.x + self.half_w, self.y + self.half_h)