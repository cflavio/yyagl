from yyagl.gameobject import Logic


class BonusLogic(Logic):

    def __init__(self, mdt, track_phys):
        Logic.__init__(self, mdt)
        self.track_phys = track_phys
        wp_info = [(w_p, (w_p.get_python_tag('initial_pos') - self.mdt.gfx.model.get_pos()).length()) for w_p in track_phys.waypoints]
        self.closest_wp = min(wp_info, key=lambda pair: pair[1])[0]
        self.closest_wp.set_pos(self.mdt.gfx.model.get_pos())
        boxes = self.closest_wp.get_python_tag('weapon_boxes')
        self.closest_wp.set_python_tag('weapon_boxes', boxes + [self.mdt])
        track_phys.redraw_wps()

    def destroy(self):
        boxes = self.closest_wp.get_python_tag('weapon_boxes')
        boxes.remove(self.mdt)
        self.closest_wp.set_python_tag('weapon_boxes', boxes)
        if self.closest_wp.get_python_tag('weapon_boxes'):
            self.closest_wp.set_pos(self.closest_wp.get_python_tag('weapon_boxes')[-1].gfx.model.get_pos())
        else:
            self.closest_wp.set_pos(self.closest_wp.get_python_tag('initial_pos'))
        self.track_phys.redraw_wps()
        self.track_phys = self.closest_wp = None
        Logic.destroy(self)
