from ..weapon.weapon import PhysWeapon
from .phys import RearRocketPhys
from .logic import RearRocketLogic
from .event import RearRocketEvent
from .ai import RearRocketAi


class RearRocket(PhysWeapon):
    phys_cls = RearRocketPhys
    logic_cls = RearRocketLogic
    event_cls = RearRocketEvent
    ai_cls = RearRocketAi
