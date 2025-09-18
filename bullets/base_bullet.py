"""
基础子弹类 - 所有子弹类型的基类
"""
import pygame
import math
import random


class BaseBullet:
    """所有子弹的基础类"""

    def __init__(self, row, col, bullet_type="base", constants=None, images=None, **kwargs):
        self.row = row
        self.col = col
        self.bullet_type = bullet_type
        self.speed = 0.09
        self.dmg = 25
        self.splash_dmg = 0

        # 状态标记
        self.can_penetrate = kwargs.get('can_penetrate', False)
        self.hit_zombies = set()  # 已击中的僵尸集合（防止重复伤害）
        self.splash_hit_zombies = set()  # 已溅射击中的僵尸集合

        # 存储引用
        self.constants = constants
        self.images = images

    def update(self, zombies_list=None):
        """更新子弹位置，返回是否应该移除"""
        self.col += self.speed
        grid_width = self.constants['GRID_WIDTH'] if self.constants else 9
        return self.col > grid_width

    def can_hit_zombie(self, zombie):
        """检查是否可以击中僵尸"""
        if zombie.is_dying:
            return False
        return abs(zombie.col - self.col) < 0.5

    def can_splash_hit_zombie(self, zombie):
        """检查僵尸是否在溅射范围内（基类默认不支持溅射）"""
        return False

    def attack_zombie(self, zombie, level_settings):
        """攻击僵尸，返回是否击中 (0=未击中, 1=击中, 2=免疫)"""
        if zombie.is_dying:
            return 0

        # 首先检查是否可以击中僵尸（距离判断）
        if not self.can_hit_zombie(zombie):
            return 0

        # 对于穿透子弹，检查是否已经击中过这个僵尸
        zombie_id = id(zombie)
        if self.can_penetrate and zombie_id in self.hit_zombies:
            return 0

        # 检查僵尸是否触发免疫
        if (hasattr(zombie, 'immunity_chance') and
                random.random() < zombie.immunity_chance):
            self.hit_zombies.add(zombie_id)
            return 2  # 免疫

        # 记录已击中的僵尸
        self.hit_zombies.add(zombie_id)

        # 造成伤害
        self._apply_damage(zombie)
        return 1

    def _apply_damage(self, zombie):
        """对僵尸造成伤害的基础方法"""
        if zombie.has_armor and zombie.armor_health > 0:
            zombie.armor_health -= self.dmg
            if zombie.armor_health < 0:
                zombie.health += zombie.armor_health  # 剩余伤害转到生命值
                zombie.armor_health = 0
        else:
            zombie.health -= self.dmg

    def apply_splash_damage(self, zombies):
        """对范围内的僵尸应用溅射伤害（基类默认不支持）"""
        return 0

    def get_display_position(self):
        """获取用于显示的位置"""
        return self.col, self.row, 0

    def draw(self, surface):
        """绘制子弹"""
        if not self.constants:
            return

        # 获取显示位置
        display_col, display_row, vertical_offset = self.get_display_position()

        x = self.constants['BATTLEFIELD_LEFT'] + int(
            display_col * (self.constants['GRID_SIZE'] + self.constants['GRID_GAP']))
        y = (self.constants['BATTLEFIELD_TOP'] +
             display_row * (self.constants['GRID_SIZE'] + self.constants['GRID_GAP']) +
             self.constants['GRID_SIZE'] // 2)

        # 应用垂直偏移（抛物线效果）
        y -= int(vertical_offset * self.constants['GRID_SIZE'])

        # 子类应该重写这个方法来绘制特定的子弹外观
        self._draw_bullet(surface, x, y)

    def _draw_bullet(self, surface, x, y):
        """绘制具体的子弹外观（子类重写）"""
        # 默认绘制一个白色圆圈
        white = self.constants.get('WHITE', (255, 255, 255)) if self.constants else (255, 255, 255)
        color = (100, 150, 255) if self.can_penetrate else white
        pygame.draw.circle(surface, color, (x, y), 5)