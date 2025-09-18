"""
僵尸基类
"""
import pygame
import random
import math


class BaseZombie:
    """所有僵尸的基类，包含通用属性和方法"""

    def __init__(self, row, has_armor_prob=0.3, is_fast=False, wave_mode=False,
                 fast_multiplier=2.5, constants=None, sounds=None, images=None,
                 level_settings=None, zombie_type="normal"):
        # 基础属性
        self.row = row
        self.col = constants['GRID_WIDTH'] if constants else 9  # 从最右侧生成
        self.zombie_type = zombie_type

        # 存储引用
        self.constants = constants
        self.sounds = sounds
        self.images = images

        # 移动和攻击属性
        self.is_fast = is_fast
        self.wave_mode = wave_mode
        self.is_attacking = False
        self.bite_timer = 0

        # 防具属性
        self.has_armor = random.random() < has_armor_prob

        # 效果相关属性
        self.immunity_chance = 0.0
        self.is_stunned = False  # 是否被眩晕
        self.is_spraying = False  # 是否正在喷射
        self.stun_visual_timer = 0  # 眩晕视觉效果计时器
        self.spray_particles = []  # 喷射粒子列表

        # 死亡动画属性
        self.is_dying = False
        self.death_animation_timer = 0
        self.death_animation_duration = 90  # 90帧 = 1.5秒
        self.current_alpha = 255
        self.death_speed_reduction = 1.0

        # 应用等级设置
        if level_settings:
            if level_settings.get("zombie_health_reduce", False):
                self.health = int(self.health * 0.8)
                self.max_health = self.health
                if self.has_armor:
                    self.armor_health = int(self.armor_health * 0.8)
                    self.max_armor_health = self.armor_health

            self.immunity_chance = 0.05 if level_settings.get("zombie_immunity", False) else 0.0

        # 计算最终速度
        self.speed = self.base_speed * (fast_multiplier if (self.wave_mode and self.is_fast) else 1)

    def start_death_animation(self):
        """开始死亡动画"""
        if not self.is_dying:
            self.is_dying = True
            self.death_animation_timer = self.death_animation_duration
            self.current_alpha = 255
            self.death_speed_reduction = 1.0
            self.is_attacking = False

    def _update_death_animation(self):
        """更新死亡动画状态"""
        self.death_animation_timer -= 1

        # 逐渐减速
        self.death_speed_reduction = max(0, self.death_speed_reduction - 0.02)
        self.col -= self.speed * self.death_speed_reduction

        # 计算透明度（从255到0线性变化）
        progress = self.death_animation_timer / self.death_animation_duration
        self.current_alpha = int(255 * progress)

        # 如果动画结束，标记为可移除
        if self.death_animation_timer <= 0:
            self.health = 0

    def update(self, plants):
        """更新僵尸状态（移动/攻击）- 基础实现"""
        if not self.constants:
            return

        # 如果处于死亡动画状态，只更新死亡动画
        if self.is_dying:
            self._update_death_animation()
            return

        # 更新眩晕视觉效果计时器
        if self.is_stunned:
            self.stun_visual_timer += 1

        # 更新喷射粒子
        if self.spray_particles:
            self.spray_particles = [p for p in self.spray_particles if p.update()]

        # 如果被眩晕，停止所有行动
        if self.is_stunned:
            return

        # 正确处理速度更新，考虑冰冻状态
        if hasattr(self, 'is_frozen') and self.is_frozen:
            # 冰冻状态下不更新速度，保持减速状态
            pass
        else:
            # 只有在非冰冻状态下才重新计算速度
            self.speed = self.base_speed * (2.5 if (self.wave_mode and self.is_fast) else 1)

        # 调用子类的具体攻击逻辑
        self._update_attack_logic(plants)

    def _update_attack_logic(self, plants):
        """子类需要实现的攻击逻辑"""
        raise NotImplementedError("子类必须实现_update_attack_logic方法")

    def set_stun_status(self, stunned: bool):
        """设置眩晕状态"""
        self.is_stunned = stunned
        if stunned:
            self.stun_visual_timer = 0

    def set_spray_status(self, spraying: bool):
        """设置喷射状态"""
        self.is_spraying = spraying

    def add_spray_particles(self, particles_count: int = 5):
        """添加喷射粒子"""
        if not self.constants:
            return

        from .effects import CucumberSprayParticle

        # 计算僵尸的像素位置
        zombie_x = (self.constants['BATTLEFIELD_LEFT'] +
                    self.col * (self.constants['GRID_SIZE'] + self.constants['GRID_GAP']) +
                    self.constants['GRID_SIZE'] // 2)
        zombie_y = (self.constants['BATTLEFIELD_TOP'] +
                    self.row * (self.constants['GRID_SIZE'] + self.constants['GRID_GAP']) +
                    self.constants['GRID_SIZE'] // 2)

        # 创建喷射粒子（向前方喷射）
        for _ in range(particles_count):
            particle = CucumberSprayParticle(zombie_x, zombie_y, direction=-1)  # 向左喷射
            self.spray_particles.append(particle)

    def draw(self, surface):
        """绘制僵尸和防具（使用图片）- 基础实现"""
        if not self.constants:
            return

        # 计算基础位置
        base_x = self.constants['BATTLEFIELD_LEFT'] + int(
            self.col * (self.constants['GRID_SIZE'] + self.constants['GRID_GAP']))
        base_y = self.constants['BATTLEFIELD_TOP'] + self.row * (
                self.constants['GRID_SIZE'] + self.constants['GRID_GAP'])

        # 根据size_multiplier计算实际大小
        actual_size = int(self.constants['GRID_SIZE'] * self.size_multiplier)

        # 居中调整位置（让大僵尸不会偏移）
        x = base_x - int((actual_size - self.constants['GRID_SIZE']) / 2)
        y = base_y - int((actual_size - self.constants['GRID_SIZE']) / 2)

        # 死亡动画：应用透明度
        if self.is_dying:
            self._draw_dying_zombie(surface, x, y, base_x, base_y, actual_size)
            return

        # 眩晕状态视觉效果：僵尸稍微摇摆
        if self.is_stunned:
            sway_amplitude = 2
            sway_frequency = 0.1
            sway_offset = int(math.sin(self.stun_visual_timer * sway_frequency) * sway_amplitude)
            x += sway_offset

        # 调用子类的具体绘制逻辑
        self._draw_zombie_body(surface, x, y, base_x, base_y, actual_size)

        # 绘制防具
        self._draw_armor(surface, x, y, actual_size)

        # 绘制血条
        self._draw_health_bars(surface, base_x, base_y, actual_size)

        # 绘制眩晕指示器
        self._draw_stun_indicator(surface, base_x, base_y, actual_size)

        # 绘制喷射粒子
        for particle in self.spray_particles:
            particle.draw(surface)

    def _draw_dying_zombie(self, surface, x, y, base_x, base_y, actual_size):
        """绘制死亡动画中的僵尸"""
        temp_surface = pygame.Surface((actual_size, actual_size), pygame.SRCALPHA)

        # 绘制僵尸本体到临时surface
        self._draw_zombie_to_surface(temp_surface, 0, 0, actual_size)

        # 应用透明度
        temp_surface.set_alpha(self.current_alpha)
        surface.blit(temp_surface, (x, y))

        # 如果有防具且防具未被摧毁，绘制防具（同样应用透明度）
        if self.has_armor and self.armor_health > 0:
            self._draw_dying_armor(surface, x, y, actual_size)

    def _draw_zombie_body(self, surface, x, y, base_x, base_y, actual_size):
        """子类需要实现的僵尸本体绘制逻辑"""
        raise NotImplementedError("子类必须实现_draw_zombie_body方法")

    def _draw_zombie_to_surface(self, surface, x, y, actual_size):
        """将僵尸绘制到指定surface（用于死亡动画）"""
        raise NotImplementedError("子类必须实现_draw_zombie_to_surface方法")

    def _draw_armor(self, surface, x, y, actual_size):
        """绘制防具"""
        if self.has_armor and self.armor_health > 0:
            if self.images and self.images.get('armor_img'):
                armor_offset = int(5 * self.size_multiplier)
                armor_size = actual_size - armor_offset * 2
                armor_x = x + armor_offset
                armor_y = y + armor_offset

                if self.zombie_type == "giant":
                    original_armor = self.images['armor_img']
                    scaled_armor = pygame.transform.scale(original_armor, (armor_size, armor_size))
                    surface.blit(scaled_armor, (armor_x, armor_y))
                else:
                    surface.blit(self.images['armor_img'], (armor_x, armor_y))

                # 如果僵尸被冰冻，在防具上也应用冰冻效果
                if hasattr(self, 'is_frozen') and self.is_frozen:
                    ice_overlay = pygame.Surface((armor_size, armor_size), pygame.SRCALPHA)
                    ice_overlay.fill((70, 130, 180, 80))
                    surface.blit(ice_overlay, (armor_x, armor_y))
            else:
                armor_offset = int(5 * self.size_multiplier)
                armor_size = actual_size - armor_offset * 2
                armor_x = x + armor_offset
                armor_y = y + armor_offset

                armor_color = self.constants['ARMOR_COLOR']
                # 如果僵尸被冰冻，防具也变成冰蓝色
                if hasattr(self, 'is_frozen') and self.is_frozen:
                    armor_color = (70, 130, 180)

                pygame.draw.rect(surface, armor_color, (armor_x, armor_y, armor_size, armor_size))

    def _draw_dying_armor(self, surface, x, y, actual_size):
        """绘制死亡动画中的防具"""
        if self.images and self.images.get('armor_img'):
            armor_offset = int(5 * self.size_multiplier)
            armor_size = actual_size - armor_offset * 2
            armor_x = x + armor_offset
            armor_y = y + armor_offset

            armor_surface = pygame.Surface((armor_size, armor_size), pygame.SRCALPHA)
            if self.zombie_type == "giant":
                original_armor = self.images['armor_img']
                scaled_armor = pygame.transform.scale(original_armor, (armor_size, armor_size))
                armor_surface.blit(scaled_armor, (0, 0))
            else:
                armor_surface.blit(self.images['armor_img'], (0, 0))

            armor_surface.set_alpha(self.current_alpha)
            surface.blit(armor_surface, (armor_x, armor_y))

    def _draw_health_bars(self, surface, base_x, base_y, actual_size):
        """绘制生命值和防具血条"""
        # 绘制僵尸血条（下方）
        health_ratio = self.health / self.max_health if self.max_health > 0 else 0
        health_bar_width = health_ratio * actual_size
        blood_bar_y = base_y + self.constants['GRID_SIZE']

        pygame.draw.rect(surface, self.constants['RED'],
                         (base_x, blood_bar_y, actual_size, 5))
        pygame.draw.rect(surface, self.constants['BLUE'],
                         (base_x, blood_bar_y, health_bar_width, 5))

        # 绘制防具血条（上方）
        if self.has_armor and self.armor_health > 0 and self.max_armor_health > 0:
            armor_ratio = self.armor_health / self.max_armor_health
            armor_bar_width = armor_ratio * actual_size
            armor_bar_y = base_y - 15

            pygame.draw.rect(surface, self.constants['RED'],
                             (base_x, armor_bar_y, actual_size, 5))
            pygame.draw.rect(surface, self.constants['ARMOR_COLOR'],
                             (base_x, armor_bar_y, armor_bar_width, 5))

    def _draw_stun_indicator(self, surface, base_x, base_y, actual_size):
        """绘制眩晕指示器"""
        if self.is_stunned:
            indicator_x = base_x + actual_size // 2
            indicator_y = base_y - 25

            star_radius = 8
            star_color = (255, 255, 0)
            rotation_speed = 0.2
            angle = self.stun_visual_timer * rotation_speed

            for i in range(3):
                offset_angle = angle + i * (2 * math.pi / 3)
                star_x = indicator_x + int(math.cos(offset_angle) * 10)
                star_y = indicator_y + int(math.sin(offset_angle) * 5)
                pygame.draw.circle(surface, star_color, (star_x, star_y), star_radius // 2)

    def _draw_ice_crystals(self, surface, x, y, actual_size):
        """绘制冰晶装饰效果"""
        # 绘制旋转的冰晶效果
        crystal_surface = pygame.Surface((actual_size, actual_size), pygame.SRCALPHA)

        # 计算旋转角度（基于时间）
        time_factor = pygame.time.get_ticks() * 0.002

        # 绘制多个小冰晶
        for i in range(6):
            angle = i * 60 + time_factor * 30  # 每60度一个冰晶，缓慢旋转
            distance = actual_size // 4

            crystal_x = actual_size // 2 + int(math.cos(math.radians(angle)) * distance)
            crystal_y = actual_size // 2 + int(math.sin(math.radians(angle)) * distance)

            # 绘制冰晶（小十字形）
            crystal_size = 3
            pygame.draw.circle(crystal_surface, (200, 230, 255, 150),
                               (crystal_x, crystal_y), crystal_size)

            # 绘制十字形光芒
            pygame.draw.line(crystal_surface, (255, 255, 255, 100),
                             (crystal_x - crystal_size, crystal_y),
                             (crystal_x + crystal_size, crystal_y), 1)
            pygame.draw.line(crystal_surface, (255, 255, 255, 100),
                             (crystal_x, crystal_y - crystal_size),
                             (crystal_x, crystal_y + crystal_size), 1)

        # 中心冰晶
        center_x, center_y = actual_size // 2, actual_size // 2
        pygame.draw.circle(crystal_surface, (255, 255, 255, 120),
                           (center_x, center_y), 4)

        surface.blit(crystal_surface, (x, y))