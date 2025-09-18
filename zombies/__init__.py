"""
僵尸模块初始化文件
"""

from .base_zombie import BaseZombie
from .normal_zombie import NormalZombie
from .giant_zombie import GiantZombie
from .zombie_factory import ZombieFactory, create_zombie
from .effects import CucumberSprayParticle

# 为了保持向后兼容，导出Zombie类
Zombie = ZombieFactory

__all__ = [
    'BaseZombie',
    'NormalZombie',
    'GiantZombie',
    'ZombieFactory',
    'create_zombie',
    'Zombie',
    'CucumberSprayParticle'
]