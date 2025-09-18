"""
数据库模块 - 统一管理游戏数据的保存和加载
"""

from .game_database import GameDatabase
from .save_manager import (
    auto_save_game_progress,
    restore_game_from_save,
    check_level_has_save
)

__all__ = [
    'GameDatabase',
    'auto_save_game_progress',
    'restore_game_from_save',
    'check_level_has_save'
]