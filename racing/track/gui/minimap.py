from direct.gui.OnscreenImage import OnscreenImage


class Minimap(object):

    def __init__(self, track, lrtb):
        self.lrtb = lrtb
        self.minimap = OnscreenImage(
            'assets/images/minimaps/%s.png' % track, pos=(-.25, 1, .25),
            scale=.2, parent=eng.base.a2dBottomRight)
        self.minimap.setTransparency(True)
        self.minimap.setAlphaScale(.64)
        self.car_handles = {}
        cars = game.fsm.race.logic.cars[:]
        cars.remove(game.player_car_name)
        cars += [game.player_car_name]
        for car_name in cars:
            scale = .015 if car_name == game.player_car_name else .01
            self.car_handles[car_name] = OnscreenImage(
                'assets/images/minimaps/car_handle.png', pos=(-.25, 1, .25),
                scale=scale, parent=eng.base.a2dBottomRight)
            col = {
                'kronos': (0, 0, 1, 1),
                'themis': (1, 0, 0, 1),
                'diones': (1, 1, 1, 1),
                'iapeto': (1, 1, 0, 1),
                }[car_name]
            self.car_handles[car_name].set_color_scale(col)
        map(lambda car: car.setTransparency(True), self.car_handles.values())
        self.width = self.minimap.getScale()[0] * 2.0
        self.height = self.minimap.getScale()[2] * 2.0
        center_x, center_y = self.minimap.getX(), self.minimap.getZ()
        self.left_img = center_x - self.width / 2.0
        self.bottom_img = center_y - self.height / 2.0

    def update(self, car_info):
        left, right, top, bottom = self.lrtb
        for car_i in car_info:
            car_name, car_pos = car_i
            pos_x_norm = (car_pos.getX() - left) / (right - left)
            pos_y_norm = (car_pos.getY() - bottom) / (top - bottom)
            pos_x = self.left_img + pos_x_norm * self.width
            pos_y = self.bottom_img + pos_y_norm * self.height
            self.car_handles[car_name].set_pos(pos_x, 1, pos_y)

    def destroy(self):
        map(lambda wdg: wdg.destroy(), [self.minimap] + self.car_handles.values())
