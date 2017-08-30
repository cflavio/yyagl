from yyagl.gameobject import GameObject
from yyagl.facade import Facade
from ..weapon.weapon import Weapon
from ..weapon.gfx import WeaponGfx
from ..weapon.audio import WeaponAudio
from .logic import RotateAllLogic
from .ai import RotateAllAi


class RotateAll(Weapon):
    logic_cls = RotateAllLogic
    ai_cls = RotateAllAi
