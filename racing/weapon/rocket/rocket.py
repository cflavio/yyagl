from ..weapon.weapon import PhysWeapon, WeaponAudio
from .phys import RocketPhys
from .logic import RocketLogic
from .event import RocketEvent
from .ai import RocketAi


class RocketAudio(WeaponAudio):
    sfx = 'assets/sfx/fire.ogg'


class Rocket(PhysWeapon):
    phys_cls = RocketPhys
    logic_cls = RocketLogic
    event_cls = RocketEvent
    ai_cls = RocketAi
    audio_cls = RocketAudio
    deg = 180
