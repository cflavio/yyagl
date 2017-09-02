from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape
from yyagl.racing.weapon.weapon.phys import WeaponPhys
from yyagl.engine.phys import PhysMgr


class MinePhys(WeaponPhys):

    cnt = 0
    coll_mesh_cls = BulletBoxShape
    joint_z = .5
    launch_dist = -2.5

    def __init__(self, mdt, car, cars):
        WeaponPhys.__init__(self, mdt, car, cars)
        MinePhys.cnt += 1
        self.coll_name = 'Mine' + str(MinePhys.cnt)
