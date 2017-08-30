from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from ..weapon.weapon import Weapon
from ..weapon.gfx import WeaponGfx
from ..weapon.audio import WeaponAudio
from .logic import TurboLogic
from .ai import TurboAi


class Turbo(Weapon):
    logic_cls = TurboLogic
    ai_cls = TurboAi
