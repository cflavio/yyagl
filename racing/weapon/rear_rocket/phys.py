from panda3d.bullet import BulletSphereShape
from yyagl.racing.weapon.weapon.phys import RocketWeaponPhys


class RearRocketPhys(RocketWeaponPhys):

    coll_mesh_cls = BulletSphereShape
    joint_z = .8
    launch_dist = -3.5
    rot_deg = 180
    rocket_coll_name = 'RearRocket'
