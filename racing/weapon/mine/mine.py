from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from ..weapon.weapon import PhysWeapon
from ..weapon.gfx import WeaponGfx
from .phys import MinePhys
from ..weapon.audio import WeaponAudio
from .logic import MineLogic
from .event import MineEvent
from .ai import MineAi


class Mine(PhysWeapon):
    phys_cls = MinePhys
    logic_cls = MineLogic
    event_cls = MineEvent
    ai_cls = MineAi