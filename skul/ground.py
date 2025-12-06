from pico2d import load_image, draw_rectangle


class Ground:
    image = None
    image_left = None
    image_right = None

    def __init__(self, x, y, w, h):
        if Ground.image is None:
            Ground.image = load_image('Grass_tile.png')
        if Ground.image_left is None:
            Ground.image_left = load_image('Grass_left_edge_tile.png')
        if Ground.image_right is None:
            Ground.image_right = load_image('Grass_right_edge_tile.png')
        self.tile_w = 32
        self.tile_h = 32
        self.x = x
        self.y = y
        self.half_w = w / 2
        self.half_h = h / 2

    def draw(self, camera_x, camera_y):
        # l_phys, b_phys, r_phys, t_phys = self.get_bb()
        #draw_rectangle(l_phys - camera_x, b_phys - camera_y, r_phys - camera_x, t_phys - camera_y)
        left_edge = self.x - self.half_w
        right_edge = self.x + self.half_w
        visual_offset_y = 5

        draw_y_center = (self.y + self.half_h) - (self.tile_h / 2) + visual_offset_y

        start_x = left_edge + (self.tile_w / 2)
        current_x = start_x

        while current_x < (right_edge + self.tile_w / 2):
            screen_x = current_x - camera_x
            screen_y = draw_y_center - camera_y

            if -50 < screen_x < 1600 + 50 and -50 < screen_y < 900 + 50:
                if current_x == start_x:
                    self.image_left.draw(screen_x, screen_y)
                elif current_x + self.tile_w >= (right_edge + self.tile_w / 2):
                    self.image_right.draw(screen_x, screen_y)
                else:
                    self.image.draw(screen_x, screen_y)

            current_x += self.tile_w

    def update(self):
        pass

    def get_bb(self):
        return (self.x - self.half_w, self.y - self.half_h,
                self.x + self.half_w, self.y + self.half_h)