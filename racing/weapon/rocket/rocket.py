from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from ..weapon.weapon import PhysWeapon
from ..weapon.gfx import WeaponGfx
from .phys import RocketPhys
from ..weapon.audio import WeaponAudio
from .logic import RocketLogic
from .event import RocketEvent
from .ai import RocketAi


class Rocket(PhysWeapon):
    phys_cls = RocketPhys
    logic_cls = RocketLogic
    event_cls = RocketEvent
    ai_cls = RocketAi
    deg = 180