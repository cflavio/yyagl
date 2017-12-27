from ..weapon.weapon import PhysWeapon, WeaponAudio
from ..weapon.gfx import WeaponGfxNetwork
from .phys import RocketPhys
from .logic import RocketLogic, RocketLogicNetwork
from .event import RocketEvent
from .ai import RocketAi


class RocketAudio(WeaponAudio):
    sfx = 'assets/sfx/fire.ogg'


class RocketGfxNetwork(WeaponGfxNetwork): pass


class Rocket(PhysWeapon):
    phys_cls = RocketPhys
    logic_cls = RocketLogic
    event_cls = RocketEvent
    ai_cls = RocketAi
    audio_cls = RocketAudio
    deg = 180


class RocketNetwork(Rocket):
    logic_cls = RocketLogicNetwork
    gfx_cls = RocketGfxNetwork
