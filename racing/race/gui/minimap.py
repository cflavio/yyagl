from direct.gui.OnscreenImage import OnscreenImage
from yyagl.gameobject import GameObject


class Minimap(GameObject):

    def __init__(self, bounds, track_img, handle_img, col_dct, cars, player_car):
        GameObject.__init__(self)
        self.bounds = bounds
        self.minimap = OnscreenImage(
            track_img, pos=(-.25, 1, .25), scale=.2,
            parent=base.a2dBottomRight)
        self.minimap.set_transparency(True)
        self.minimap.set_alpha_scale(.64)
        self.car_handles = {}
        for car_name in sorted(cars, key=lambda car: car == player_car):
            self.__set_car(car_name, player_car, handle_img, col_dct)
        list(map(lambda car: car.set_transparency(True), self.car_handles.values()))
        self.width = self.minimap.get_scale()[0] * 2.0
        self.height = self.minimap.get_scale()[2] * 2.0
        center_x, center_y = self.minimap.get_x(), self.minimap.get_z()
        self.left_img = center_x - self.width / 2.0
        self.bottom_img = center_y - self.height / 2.0

    def __set_car(self, car_name, player_car, handle_img, col_dct):
        scale = .015 if car_name == player_car else .01
        self.car_handles[car_name] = OnscreenImage(
            handle_img, pos=(-.25, 1, .25), scale=scale,
            parent=base.a2dBottomRight)
        self.car_handles[car_name].set_color_scale(col_dct[car_name])

    def update(self, car_info):
        list(map(self.__update_car, car_info))

    def __update_car(self, car_i):
        left, right, top, bottom = self.bounds
        car_name, car_pos = car_i
        pos_x_norm = (car_pos.get_x() - left) / (right - left)
        pos_y_norm = (car_pos.get_y() - bottom) / (top - bottom)
        pos_x = self.left_img + pos_x_norm * self.width
        pos_y = self.bottom_img + pos_y_norm * self.height
        self.car_handles[car_name].set_pos(pos_x, 1, pos_y)

    def destroy(self):
        des = lambda wdg: wdg.destroy()
        list(map(des, [self.minimap] + list(self.car_handles.values())))
        GameObject.destroy(self)
