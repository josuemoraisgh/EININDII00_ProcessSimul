
from dataclasses import dataclass

@dataclass
class UIConfig:
    CONTROL_PANEL_WIDTH: int = 300
    LEFT_MARGIN: float = 0.08
    RIGHT_MARGIN: float = 0.94
    LABELPAD: int = 3
    TICK_PAD: int = 2
