from ..weapon.weapon import Weapon
from .logic import RotateAllLogic
from .ai import RotateAllAi


class RotateAll(Weapon):
    logic_cls = RotateAllLogic
    ai_cls = RotateAllAi
