from yyagl.gameobject import LogicColleague


class BonusLogic(LogicColleague):

    def __init__(self, mdt, track_phys):
        LogicColleague.__init__(self, mdt)
        self.track_phys = track_phys
        pos = self.mdt.gfx.model.get_pos()
        wp_info = [
            (w_p, (w_p.get_python_tag('initial_pos') - pos).length())
            for w_p in track_phys.wp2prevs]
        self.closest_wp = min(wp_info, key=lambda pair: pair[1])[0]
        self.closest_wp.set_pos(self.mdt.gfx.model.get_pos())
        boxes = self.closest_wp.get_python_tag('weapon_boxes')
        self.closest_wp.set_python_tag('weapon_boxes', boxes + [self.mdt])
        track_phys.redraw_wps()

    def destroy(self):
        cwp = self.closest_wp
        boxes = cwp.get_python_tag('weapon_boxes')
        boxes.remove(self.mdt)
        cwp.set_python_tag('weapon_boxes', boxes)
        if cwp.get_python_tag('weapon_boxes'):
            weap_boxes = cwp.get_python_tag('weapon_boxes')
            cwp.set_pos(weap_boxes[-1].gfx.model.get_pos())
        else:
            cwp.set_pos(cwp.get_python_tag('initial_pos'))
        self.track_phys.redraw_wps()
        self.track_phys = self.closest_wp = None
        LogicColleague.destroy(self)
