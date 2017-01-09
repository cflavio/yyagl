from os.path import exists
from yyagl.gameobject import Event
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape, \
    BulletSphereShape, BulletGhostNode
from panda3d.core import Mat4


class BonusEvent(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.generate_tsk = None

    def on_collision(self, obj, obj_name):
        if obj_name == 'Bonus' and obj in self.mdt.phys.ghost.getOverlappingNodes():
            pos = self.mdt.phys.pos
            game.track.phys.bonuses.remove(self.mdt)
            self.mdt.destroy()
            self.generate_tsk = taskMgr.doMethodLater(20, lambda tsk: game.track.phys.create_bonus(pos), 'create bonus')

    def destroy(self):
        Event.destroy(self)
        if self.generate_tsk:
            taskMgr.remove_task(self.generate_tsk)