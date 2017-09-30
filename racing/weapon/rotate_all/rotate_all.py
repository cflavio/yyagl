from ..weapon.weapon import Weapon, WeaponAudio
from .logic import RotateAllLogic
from .ai import RotateAllAi


class RotateAllAudio(WeaponAudio):
    sfx = 'assets/sfx/rotate_all_fire.ogg'


class RotateAll(Weapon):
    logic_cls = RotateAllLogic
    ai_cls = RotateAllAi
    audio_cls = RotateAllAudio
