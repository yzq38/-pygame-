"""
植物模块 - 统一导出所有植物类
"""

# 导入基础类
from .base_plant import BasePlant
from .shooter_base import ShooterPlant

# 导入粒子效果
from .particles import (
    ExplosionParticle,
    CucumberExplosionParticle,
    CucumberSprayParticle
)

# 导入所有植物类
from .sunflower import Sunflower
from .shooter import Shooter
from .wall_nut import WallNut
from .cherry_bomb import CherryBomb
from .cucumber import Cucumber
from .melon_pult import MelonPult
from .cattail import Cattail
from .dandelion import Dandelion
from .ice_cactus import IceCactus
from .lightning_flower import LightningFlower


# 植物工厂函数 - 保持向后兼容
def Plant(row, col, plant_type=None, constants=None, images=None, level_manager=None):
    """
    植物工厂函数 - 根据类型创建对应的植物实例
    保持与原代码的兼容性
    """
    if plant_type == "sunflower":
        return Sunflower(row, col, constants, images, level_manager)
    elif plant_type == "shooter":
        return Shooter(row, col, constants, images, level_manager)
    elif plant_type == "wall_nut":
        return WallNut(row, col, constants, images, level_manager)
    elif plant_type == "cherry_bomb":
        return CherryBomb(row, col, constants, images, level_manager)
    elif plant_type == "cucumber":
        return Cucumber(row, col, constants, images, level_manager)
    elif plant_type == "melon_pult":
        return MelonPult(row, col, constants, images, level_manager)
    elif plant_type == "cattail":
        return Cattail(row, col, constants, images, level_manager)
    elif plant_type == "dandelion":
        return Dandelion(row, col, constants, images, level_manager)
    elif plant_type == "ice_cactus":
        return IceCactus(row, col, constants, images, level_manager)
    elif plant_type == "lightning_flower":
        return LightningFlower(row, col, constants, images, level_manager)
    else:
        # 默认返回基础植物
        return BasePlant(row, col, plant_type, constants, images, level_manager)


# 导出所有需要的类和函数
__all__ = [
    # 基础类
    'BasePlant',
    'ShooterPlant',

    # 粒子效果
    'ExplosionParticle',
    'CucumberExplosionParticle',
    'CucumberSprayParticle',

    # 植物类
    'Sunflower',
    'Shooter',
    'WallNut',
    'CherryBomb',
    'cucumber.py',
    'MelonPult',
    'Cattail',
    'Dandelion',
    'IceCactus',
    'LightningFlower',

    # 工厂函数
    'Plant',
]