from ..weapon.weapon import PhysWeapon
from .phys import MinePhys
from .logic import MineLogic
from .event import MineEvent
from .ai import MineAi


class Mine(PhysWeapon):
    phys_cls = MinePhys
    logic_cls = MineLogic
    event_cls = MineEvent
    ai_cls = MineAi
