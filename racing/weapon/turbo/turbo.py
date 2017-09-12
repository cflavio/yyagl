from ..weapon.weapon import Weapon
from .logic import TurboLogic
from .ai import TurboAi


class Turbo(Weapon):
    logic_cls = TurboLogic
    ai_cls = TurboAi
