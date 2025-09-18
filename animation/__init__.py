"""
动画模块 - 统一管理所有动画效果
"""
from .manager import AnimationManager
from .plant_flying import PlantFlyingAnimation
from .menu import MenuAnimationHandler
from .effects import AnimationEffects
from .trophy import Trophy

__all__ = [
    'AnimationManager',
    'PlantFlyingAnimation',
    'MenuAnimationHandler',
    'AnimationEffects',
    'Trophy'
]