from ..weapon.weapon import PhysWeapon, WeaponAudio
from ..weapon.gfx import WeaponGfxNetwork
from .phys import MinePhys
from .logic import MineLogic, MineLogicNetwork
from .event import MineEvent
from .ai import MineAi


class MineGfxNetwork(WeaponGfxNetwork): pass


class MineAudio(WeaponAudio):
    sfx = 'assets/sfx/mine.ogg'


class Mine(PhysWeapon):
    phys_cls = MinePhys
    logic_cls = MineLogic
    event_cls = MineEvent
    audio_cls = MineAudio
    ai_cls = MineAi


class MineNetwork(Mine):
    logic_cls = MineLogicNetwork
    gfx_cls = MineGfxNetwork
