# core/__init__.py
"""
游戏核心模块包
包含游戏的核心逻辑、管理器和基础组件
"""

# 导出主要的管理器和工厂函数，方便外部导入
from .cards_manager import cards_manager, get_available_cards_new, get_plant_select_grid_new
from .features_manager import features_manager
from .game_state_manager import GameStateManager
from .level_manager import LevelManager
from .event_handler import EventHandler
from .constants import *

__all__ = [
    'cards_manager',
    'get_available_cards_new',
    'get_plant_select_grid_new',
    'features_manager',
    'GameStateManager',
    'LevelManager',
    'EventHandler',
    # constants中的所有内容会通过 * 导入
]
