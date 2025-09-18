"""
豌豆子弹类 - 基础攻击子弹
"""
import pygame
from .base_bullet import BaseBullet


class PeaBullet(BaseBullet):
    """豌豆子弹类 - 植物大战僵尸的基础子弹"""

    def __init__(self, row, col, can_penetrate=False, constants=None, images=None, **kwargs):
        super().__init__(row, col, bullet_type="pea", constants=constants, images=images, **kwargs)

        # 豌豆子弹属性
        self.speed = 0.09
        self.dmg = 25  # 豌豆伤害
        self.splash_dmg = 0  # 豌豆没有溅射伤害
        self.can_penetrate = can_penetrate

    def can_hit_zombie(self, zombie):
        """豌豆子弹的碰撞检测"""
        if zombie.is_dying:
            return False
        return zombie.row == self.row and abs(zombie.col - self.col) < 0.5

    def _draw_bullet(self, surface, x, y):
        """绘制豌豆子弹"""
        # 尝试使用豌豆图片
        pea_img = self.images.get('pea_img') if self.images else None
        if pea_img:
            surface.blit(pea_img, (x - 10, y - 10))
        else:
            # 没有图片时使用颜色圆圈
            white = self.constants.get('WHITE', (255, 255, 255)) if self.constants else (255, 255, 255)
            color = (100, 150, 255) if self.can_penetrate else white  # 穿透豌豆是蓝色
            pygame.draw.circle(surface, color, (x, y), 5)