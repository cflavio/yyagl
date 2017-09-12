from ..weapon.weapon import PhysWeapon
from .phys import RocketPhys
from .logic import RocketLogic
from .event import RocketEvent
from .ai import RocketAi


class Rocket(PhysWeapon):
    phys_cls = RocketPhys
    logic_cls = RocketLogic
    event_cls = RocketEvent
    ai_cls = RocketAi
    deg = 180
