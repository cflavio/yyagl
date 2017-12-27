from ..weapon.weapon import PhysWeapon, WeaponAudio
from ..weapon.gfx import WeaponGfxNetwork
from .phys import RearRocketPhys
from .logic import RearRocketLogic, RearRocketLogicNetwork
from .event import RearRocketEvent
from .ai import RearRocketAi


class RearRocketAudio(WeaponAudio):
    sfx = 'assets/sfx/fire.ogg'


class RearRocketGfxNetwork(WeaponGfxNetwork): pass


class RearRocket(PhysWeapon):
    phys_cls = RearRocketPhys
    logic_cls = RearRocketLogic
    event_cls = RearRocketEvent
    ai_cls = RearRocketAi
    audio_cls = RearRocketAudio


class RearRocketNetwork(RearRocket):
    logic_cls = RearRocketLogicNetwork
    gfx_cls = RearRocketGfxNetwork
