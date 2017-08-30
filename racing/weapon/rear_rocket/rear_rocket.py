from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from ..weapon.weapon import PhysWeapon
from ..weapon.gfx import WeaponGfx
from .phys import RearRocketPhys
from ..weapon.audio import WeaponAudio
from .logic import RearRocketLogic
from .event import RearRocketEvent
from .ai import RearRocketAi


class RearRocket(PhysWeapon):
    phys_cls = RearRocketPhys
    logic_cls = RearRocketLogic
    event_cls = RearRocketEvent
    ai_cls = RearRocketAi
