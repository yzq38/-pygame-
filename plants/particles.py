"""
植物相关的粒子效果类
"""
import pygame
import random
import math


class ExplosionParticle:
    """樱桃炸弹爆炸粒子 - 改进版：扩散效果，无重力"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(8, 18)
        self.max_radius = self.radius

        # 随机方向（360度）和速度
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.friction = 0.98  # 摩擦系数

        # 爆炸颜色
        colors = [
            (255, 80, 80),
            (255, 120, 40),
            (255, 160, 0),
            (255, 200, 0),
            (255, 255, 100),
            (255, 200, 200),
            (255, 100, 0),
        ]
        self.color = random.choice(colors)

        self.life = random.randint(30, 60)
        self.max_life = self.life
        self.alpha = 255

        self.rotation = 0
        self.rotation_speed = random.uniform(-8, 8)
        self.scale_factor = 1.0
        self.pulse_speed = random.uniform(0.05, 0.15)

    def update(self):
        self.vx *= self.friction
        self.vy *= self.friction

        self.x += self.vx
        self.y += self.vy

        self.rotation += self.rotation_speed

        self.life -= 1
        life_ratio = self.life / self.max_life

        # 大小变化
        if life_ratio > 0.8:
            expansion = 1.0 + (1 - life_ratio) * 5
            self.scale_factor = expansion
        elif life_ratio > 0.3:
            pulse = 1.0 + math.sin(self.life * self.pulse_speed) * 0.1
            self.scale_factor = 1.3 * pulse
        else:
            self.scale_factor = life_ratio * 1.3

        self.radius = max(1, int(self.max_radius * self.scale_factor))

        # 透明度变化
        if life_ratio > 0.5:
            self.alpha = 255
        else:
            self.alpha = int(255 * (life_ratio / 0.5))

        return self.life > 0

    def draw(self, surface):
        if self.radius > 0 and self.alpha > 0:
            particle_size = self.radius * 2
            particle_surface = pygame.Surface((particle_size, particle_size), pygame.SRCALPHA)

            color_with_alpha = (*self.color, self.alpha)
            pygame.draw.circle(particle_surface, color_with_alpha,
                               (self.radius, self.radius), self.radius)

            if self.radius > 4:
                highlight_radius = max(1, self.radius // 3)
                highlight_alpha = min(self.alpha, 180)
                highlight_color = (255, 255, 255, highlight_alpha)
                highlight_offset = max(1, self.radius // 4)
                pygame.draw.circle(particle_surface, highlight_color,
                                   (self.radius - highlight_offset, self.radius - highlight_offset),
                                   highlight_radius)

            if abs(self.rotation) > 0.1:
                particle_surface = pygame.transform.rotate(particle_surface, self.rotation)

            draw_x = self.x - particle_surface.get_width() // 2
            draw_y = self.y - particle_surface.get_height() // 2

            surface.blit(particle_surface, (draw_x, draw_y))


class CucumberExplosionParticle:
    """黄瓜爆炸粒子 - 绿色系波动"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(6, 15)
        self.max_radius = self.radius

        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.friction = 0.97

        # 绿色调色板
        colors = [
            (144, 238, 144),
            (152, 251, 152),
            (173, 255, 47),
            (127, 255, 0),
            (124, 252, 0),
            (50, 205, 50),
            (34, 139, 34),
        ]
        self.color = random.choice(colors)

        self.life = random.randint(35, 70)
        self.max_life = self.life
        self.alpha = 255

        self.rotation = 0
        self.rotation_speed = random.uniform(-6, 6)
        self.scale_factor = 1.0
        self.pulse_speed = random.uniform(0.08, 0.18)

    def update(self):
        self.vx *= self.friction
        self.vy *= self.friction

        self.x += self.vx
        self.y += self.vy

        self.rotation += self.rotation_speed

        self.life -= 1
        life_ratio = self.life / self.max_life

        if life_ratio > 0.8:
            expansion = 1.0 + (1 - life_ratio) * 4
            self.scale_factor = expansion
        elif life_ratio > 0.4:
            pulse = 1.0 + math.sin(self.life * self.pulse_speed) * 0.12
            self.scale_factor = 1.2 * pulse
        else:
            self.scale_factor = life_ratio * 1.2

        self.radius = max(1, int(self.max_radius * self.scale_factor))

        if life_ratio > 0.6:
            self.alpha = 255
        else:
            self.alpha = int(255 * (life_ratio / 0.6))

        return self.life > 0

    def draw(self, surface):
        if self.radius > 0 and self.alpha > 0:
            particle_size = self.radius * 2
            particle_surface = pygame.Surface((particle_size, particle_size), pygame.SRCALPHA)

            color_with_alpha = (*self.color, self.alpha)
            pygame.draw.circle(particle_surface, color_with_alpha,
                               (self.radius, self.radius), self.radius)

            if self.radius > 4:
                highlight_radius = max(1, self.radius // 3)
                highlight_alpha = min(self.alpha, 160)
                highlight_color = (255, 255, 255, highlight_alpha)
                highlight_offset = max(1, self.radius // 4)
                pygame.draw.circle(particle_surface, highlight_color,
                                   (self.radius - highlight_offset, self.radius - highlight_offset),
                                   highlight_radius)

            if abs(self.rotation) > 0.1:
                particle_surface = pygame.transform.rotate(particle_surface, self.rotation)

            draw_x = self.x - particle_surface.get_width() // 2
            draw_y = self.y - particle_surface.get_height() // 2

            surface.blit(particle_surface, (draw_x, draw_y))


class CucumberSprayParticle:
    """黄瓜喷射粒子 - 乳白色，向前喷射"""

    def __init__(self, x, y, direction=1):
        self.x = x
        self.y = y
        self.radius = random.randint(3, 8)
        self.max_radius = self.radius

        self.direction = direction

        forward_speed = random.uniform(3, 6)
        vertical_spread = random.uniform(-1, 1)

        self.vx = forward_speed * self.direction
        self.vy = vertical_spread

        self.gravity = 0.1
        self.friction = 0.98

        # 乳白色调色板
        base_colors = [
            (255, 255, 240),
            (250, 250, 210),
            (255, 250, 240),
            (248, 248, 255),
            (240, 248, 255),
        ]
        self.color = random.choice(base_colors)

        self.life = random.randint(100, 140)
        self.max_life = self.life
        self.alpha = 220

        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        self.pulse_speed = random.uniform(0.1, 0.2)

    def update(self):
        self.vy += self.gravity
        self.vx *= self.friction
        self.vy *= self.friction

        self.x += self.vx
        self.y += self.vy

        self.rotation += self.rotation_speed

        self.life -= 1
        life_ratio = self.life / self.max_life

        if life_ratio > 0.7:
            scale = 1.0 + (1 - life_ratio) * 0.5
            self.alpha = 220
        elif life_ratio > 0.3:
            pulse = 1.0 + math.sin(self.life * self.pulse_speed) * 0.15
            scale = 1.2 * pulse
            self.alpha = int(200 * life_ratio)
        else:
            scale = life_ratio * 1.2
            self.alpha = int(150 * life_ratio)

        self.radius = max(1, int(self.max_radius * scale))

        return self.life > 0

    def draw(self, surface):
        if self.radius > 0 and self.alpha > 0:
            particle_size = self.radius * 2
            particle_surface = pygame.Surface((particle_size, particle_size), pygame.SRCALPHA)

            color_with_alpha = (*self.color, self.alpha)
            pygame.draw.circle(particle_surface, color_with_alpha,
                               (self.radius, self.radius), self.radius)

            if self.radius > 3:
                highlight_radius = max(1, self.radius // 2)
                highlight_alpha = min(self.alpha // 2, 100)
                highlight_color = (255, 255, 255, highlight_alpha)
                pygame.draw.circle(particle_surface, highlight_color,
                                   (self.radius, self.radius), highlight_radius)

            if abs(self.rotation) > 0.1:
                particle_surface = pygame.transform.rotate(particle_surface, self.rotation)

            draw_x = self.x - particle_surface.get_width() // 2
            draw_y = self.y - particle_surface.get_height() // 2

            surface.blit(particle_surface, (draw_x, draw_y))