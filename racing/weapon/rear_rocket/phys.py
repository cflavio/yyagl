from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape
from panda3d.core import Mat4, BitMask32
from yyagl.racing.weapon.weapon.phys import RocketWeaponPhys
from yyagl.engine.phys import PhysMgr


class RearRocketPhys(RocketWeaponPhys):

    coll_mesh_cls = BulletSphereShape
    joint_z = .8
    launch_dist = -3.5
    rot_deg = 180
    rocket_coll_name = 'RearRocket'
