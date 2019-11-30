from panda3d.bullet import BulletBoxShape
from yyagl.racing.weapon.weapon.phys import WeaponPhys


class MinePhys(WeaponPhys):

    cnt = 0
    coll_mesh_cls = BulletBoxShape
    joint_z = .5
    gfx_dz = -.45
    launch_dist = -2.5

    def __init__(self, mediator, car, cars, players):
        WeaponPhys.__init__(self, mediator, car, cars, players)
        MinePhys.cnt += 1
        self.coll_name = 'Mine' + str(MinePhys.cnt)
