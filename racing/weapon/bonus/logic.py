from yyagl.gameobject import LogicColleague
from yyagl.engine.vec import Vec


class BonusLogic(LogicColleague):

    def __init__(self, mediator, track_phys, track_gfx):
        LogicColleague.__init__(self, mediator)
        self.track_phys = track_phys
        self.track_gfx = track_gfx
        pos = self.mediator.gfx.model.get_pos()
        wp_info = [
            (w_p, (w_p.initial_pos - pos).length())
            for w_p in track_phys.waypoints]
        self.closest_wp = min(wp_info, key=lambda pair: pair[1])[0]
        pos = self.mediator.gfx.model.get_pos()
        pos = Vec(pos.x, pos.y, pos.z)
        self.closest_wp.node.set_pos(pos)
        self.closest_wp.weapon_boxes += [self.mediator]
        track_gfx.redraw_wps()

    def destroy(self):
        cwp = self.closest_wp
        boxes = cwp.weapon_boxes
        boxes.remove(self.mediator)
        cwp.weapon_boxes = boxes
        if cwp.weapon_boxes:
            pos = cwp.weapon_boxes[-1].gfx.model.get_pos()
            pos = Vec(pos.x, pos.y, pos.z)
            cwp.node.set_pos(pos)
        else:
            pos = cwp.initial_pos
            pos = Vec(pos.x, pos.y, pos.z)
            cwp.node.set_pos(pos)
        self.track_gfx.redraw_wps()
        self.track_phys = self.track_gfx = self.closest_wp = None
        LogicColleague.destroy(self)
