from ..weapon.weapon import PhysWeapon
from ..weapon.gfx import WeaponGfxNetwork
from .phys import MinePhys
from .logic import MineLogic, MineLogicNetwork
from .event import MineEvent
from .ai import MineAi


class MineGfxNetwork(WeaponGfxNetwork): pass


class Mine(PhysWeapon):
    phys_cls = MinePhys
    logic_cls = MineLogic
    event_cls = MineEvent
    ai_cls = MineAi


class MineNetwork(Mine):
    logic_cls = MineLogicNetwork
    gfx_cls = MineGfxNetwork
