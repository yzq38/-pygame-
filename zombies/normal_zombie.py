"""
普通僵尸类
"""
import pygame
from .base_zombie import BaseZombie


class NormalZombie(BaseZombie):
    """普通僵尸实现"""

    def __init__(self, row, has_armor_prob=0.3, is_fast=False, wave_mode=False,
                 fast_multiplier=2.5, constants=None, sounds=None, images=None,
                 level_settings=None):
        # 设置普通僵尸的基础属性
        self.health = 150
        self.max_health = 150
        self.base_speed = 0.004
        self.attack_dmg = 1
        self.size_multiplier = 1.0

        # 调用父类构造函数
        super().__init__(row, has_armor_prob, is_fast, wave_mode, fast_multiplier,
                         constants, sounds, images, level_settings, "normal")

        # 设置防具血量
        # 波次模式下快速铁门血量变为300
        self.armor_health = 300 if (self.has_armor and wave_mode and is_fast) else (200 if self.has_armor else 0)
        self.max_armor_health = self.armor_health

    def _update_attack_logic(self, plants):
        """普通僵尸的攻击逻辑（原有逻辑）"""
        # 未攻击时移动
        if not self.is_attacking:
            self.col -= self.speed

        # 检测是否碰撞植物（同列同排）
        self.is_attacking = False
        for plant in plants:
            if plant.row == self.row and abs(self.col - plant.col) < 0.5:
                self.is_attacking = True

                # 修复：使用植物的 take_damage 方法而不是直接修改血量
                plant.take_damage(self.attack_dmg)

                # 控制啃咬音效播放（每0.5秒一次）
                bite_interval = self.constants.get('BITE_INTERVAL', 30)
                self.bite_timer += 1
                if self.bite_timer >= bite_interval:
                    if self.sounds and self.sounds.get("bite"):
                        self.sounds["bite"].play()
                    self.bite_timer = 0

                # 修复：检查植物是否死亡，使用统一的死亡判断方法
                if not plant.is_alive():
                    plants.remove(plant)  # 植物死亡移除
                break

    def _draw_zombie_body(self, surface, x, y, base_x, base_y, actual_size):
        """绘制普通僵尸本体"""
        if self.images and self.images.get('zombie_img'):
            zombie_img = self.images['zombie_img']

            # 修复：改进冰冻效果处理
            if hasattr(self, 'is_frozen') and self.is_frozen:
                # 先绘制原图
                surface.blit(zombie_img, (base_x, base_y))

                # 创建海蓝色冰冻覆盖层
                ice_overlay = pygame.Surface((actual_size, actual_size), pygame.SRCALPHA)
                ice_overlay.fill((70, 130, 180, 120))  # 海蓝色
                surface.blit(ice_overlay, (x, y))

                # 绘制冰晶效果
                self._draw_ice_crystals(surface, x, y, actual_size)

            elif self.is_stunned:
                stun_surface = zombie_img.copy()
                stun_surface.fill((255, 255, 0, 100), special_flags=pygame.BLEND_ADD)
                surface.blit(stun_surface, (base_x, base_y))
            else:
                surface.blit(zombie_img, (base_x, base_y))
        else:
            # 没有图片时使用矩形
            color = self.constants['GRAY']

            # 根据状态改变颜色
            if hasattr(self, 'is_frozen') and self.is_frozen:
                color = (70, 130, 180)  # 海蓝色表示冰冻
            elif self.is_stunned:
                color = (255, 255, 0)  # 黄色表示眩晕

            pygame.draw.rect(surface, color, (x, y, actual_size, actual_size))

    def _draw_zombie_to_surface(self, surface, x, y, actual_size):
        """将僵尸绘制到指定surface（用于死亡动画）"""
        if self.images and self.images.get('zombie_img'):
            surface.blit(self.images['zombie_img'], (x, y))
        else:
            color = self.constants.get('GRAY', (128, 128, 128))
            pygame.draw.rect(surface, color, (x, y, actual_size, actual_size))