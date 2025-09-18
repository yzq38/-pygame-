"""
子弹系统模块 - 包含各种子弹类型
"""

from .base_bullet import BaseBullet
from .pea_bullet import PeaBullet
from .melon_bullet import MelonBullet
from .spike_bullet import SpikeBullet
from .ice_bullet import IceBullet
from .dandelion_seed import DandelionSeed


# 工厂函数，用于创建不同类型的子弹
def create_bullet(bullet_type, row, col, **kwargs):
    """
    根据类型创建相应的子弹对象

    Args:
        bullet_type: 子弹类型 ("pea", "melon", "spike", "ice")
        row: 行位置
        col: 列位置
        **kwargs: 其他参数

    Returns:
        对应类型的子弹对象
    """
    bullet_classes = {
        "pea": PeaBullet,
        "melon": MelonBullet,
        "spike": SpikeBullet,
        "ice": IceBullet
    }

    bullet_class = bullet_classes.get(bullet_type, PeaBullet)
    return bullet_class(row, col, **kwargs)


__all__ = [
    'BaseBullet',
    'PeaBullet',
    'MelonBullet',
    'SpikeBullet',
    'IceBullet',
    'DandelionSeed',
    'create_bullet'
]