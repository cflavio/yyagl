from ..weapon.weapon import Weapon, WeaponAudio
from .logic import TurboLogic, TurboLogicNetwork
from .ai import TurboAi


class TurboAudio(WeaponAudio):
    sfx = 'assets/sfx/turbo.ogg'


class Turbo(Weapon):
    logic_cls = TurboLogic
    ai_cls = TurboAi
    audio_cls = TurboAudio

class TurboNetwork(Turbo):
    logic_cls = TurboLogicNetwork
