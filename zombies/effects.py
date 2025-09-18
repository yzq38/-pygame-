"""
僵尸相关的视觉效果
"""
import pygame
import random
import math


class CucumberSprayParticle:
    """黄瓜喷射粒子 - 乳白色，向前喷射"""

    def __init__(self, x, y, direction=1):
        self.x = x
        self.y = y
        self.radius = random.randint(3, 8)
        self.max_radius = self.radius

        # 向前喷射（方向由僵尸朝向决定）
        self.direction = direction  # 1向右，-1向左

        # 主要向前，稍微有些散射
        forward_speed = random.uniform(1, 3)
        vertical_spread = random.uniform(-0.5, 0.5)

        self.vx = forward_speed * self.direction
        self.vy = vertical_spread

        # 重力和空气阻力
        self.gravity = 0.1
        self.friction = 0.98

        # 乳白色色调色板
        base_colors = [
            (255, 255, 240),  # 象牙白
            (250, 250, 210),  # 淡黄白
            (255, 250, 240),  # 花白
            (248, 248, 255),  # 幽灵白
            (240, 248, 255),  # 爱丽丝蓝白
        ]
        self.color = random.choice(base_colors)

        # 生命周期：2秒 = 120帧
        self.life = random.randint(80, 120)
        self.max_life = self.life
        self.alpha = 220

        # 旋转和脉冲效果
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        self.pulse_speed = random.uniform(0.1, 0.2)

    def update(self):
        # 应用重力和阻力
        self.vy += self.gravity
        self.vx *= self.friction
        self.vy *= self.friction

        # 更新位置
        self.x += self.vx
        self.y += self.vy

        # 更新旋转
        self.rotation += self.rotation_speed

        # 减少生命值
        self.life -= 1
        life_ratio = self.life / self.max_life

        # 大小和透明度变化
        if life_ratio > 0.7:
            # 初期：稍微增大
            scale = 1.0 + (1 - life_ratio) * 0.5
            self.alpha = 220
        elif life_ratio > 0.3:
            # 中期：稳定大小，轻微脉冲
            pulse = 1.0 + math.sin(self.life * self.pulse_speed) * 0.15
            scale = 1.2 * pulse
            self.alpha = int(200 * life_ratio)
        else:
            # 后期：缩小并变透明
            scale = life_ratio * 1.2
            self.alpha = int(150 * life_ratio)

        self.radius = max(1, int(self.max_radius * scale))

        return self.life > 0

    def draw(self, surface):
        if self.radius > 0 and self.alpha > 0:
            particle_size = self.radius * 2
            particle_surface = pygame.Surface((particle_size, particle_size), pygame.SRCALPHA)

            # 绘制主体粒子
            color_with_alpha = (*self.color, self.alpha)
            pygame.draw.circle(particle_surface, color_with_alpha,
                               (self.radius, self.radius), self.radius)

            # 添加柔和的内部高光
            if self.radius > 3:
                highlight_radius = max(1, self.radius // 2)
                highlight_alpha = min(self.alpha // 2, 100)
                highlight_color = (255, 255, 255, highlight_alpha)
                pygame.draw.circle(particle_surface, highlight_color,
                                   (self.radius, self.radius), highlight_radius)

            # 应用旋转
            if abs(self.rotation) > 0.1:
                particle_surface = pygame.transform.rotate(particle_surface, self.rotation)

            # 计算绘制位置
            draw_x = self.x - particle_surface.get_width() // 2
            draw_y = self.y - particle_surface.get_height() // 2

            surface.blit(particle_surface, (draw_x, draw_y))