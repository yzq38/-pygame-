"""
小推车类 - 处理小推车的移动、碰撞和渲染
"""
import pygame
import sys
import os



from core.constants import *


class Cart:
    """小推车类"""

    def __init__(self, row, images=None, sounds=None):
        self.row = row  # 小推车所在行
        self.col = -0.5  # 初始位置在战场左侧
        self.speed = 0.08  # 移动速度（每帧移动的格子数）
        self.active = False  # 是否已被激活
        self.triggered = False  # 是否已被触发（点击或僵尸触发）
        self.removed = False  # 是否应该被移除

        # 图片和声音资源
        self.images = images
        self.sounds = sounds

        # 碰撞检测相关
        self.width = 30
        self.height = 30

        # 音效播放控制
        self.sound_played = False

    def trigger(self):
        """触发小推车（点击或僵尸接近时调用）"""
        if not self.triggered and not self.removed:
            self.triggered = True
            self.active = True

            # 播放小推车触发音效
            if self.sounds and self.sounds.get("cart_trigger") and not self.sound_played:
                self.sounds["cart_trigger"].play()
                self.sound_played = True

    def update(self, zombies):
        """更新小推车状态"""
        if not self.active or self.removed:
            return []

        # 向右移动
        self.col += self.speed

        # 检查与僵尸的碰撞
        hit_zombies = []
        for zombie in zombies:
            if zombie.row == self.row and not zombie.is_dying:
                # 检查碰撞（小推车和僵尸的距离）
                distance = abs(zombie.col - self.col)
                if distance < 0.3:  # 碰撞检测阈值
                    hit_zombies.append(zombie)

        # 如果移出屏幕右侧，标记为可移除
        if self.col > GRID_WIDTH + 2:
            self.removed = True

        return hit_zombies

    def get_screen_position(self):
        """获取小推车在屏幕上的像素坐标"""
        screen_x = BATTLEFIELD_LEFT + self.col * (GRID_SIZE + GRID_GAP)
        screen_y = BATTLEFIELD_TOP + self.row * (GRID_SIZE + GRID_GAP) + (GRID_SIZE - 30) // 2
        return screen_x, screen_y

    def get_click_rect(self):
        """获取小推车的点击区域（未触发时）"""
        if self.triggered or self.removed:
            return None

        # 初始位置的点击区域
        cart_x = BATTLEFIELD_LEFT - 40
        cart_y = BATTLEFIELD_TOP + self.row * (GRID_SIZE + GRID_GAP) + (GRID_SIZE - 30) // 2
        return pygame.Rect(cart_x, cart_y, 30, 30)

    def draw(self, surface):
        """绘制小推车"""
        if self.removed:
            return

        screen_x, screen_y = self.get_screen_position()

        # 如果已触发，绘制在移动位置；否则绘制在初始位置
        if self.triggered:
            draw_x = screen_x
            draw_y = screen_y
        else:
            # 未触发时绘制在战场左侧
            draw_x = BATTLEFIELD_LEFT - 40
            draw_y = BATTLEFIELD_TOP + self.row * (GRID_SIZE + GRID_GAP) + (GRID_SIZE - 30) // 2

        # 确保不绘制到屏幕外
        if draw_x < -50 or draw_x > BASE_WIDTH + 50:
            return

        # 获取小推车图片
        if self.images and self.images.get('cart_img'):
            cart_img = pygame.transform.scale(self.images['cart_img'], (30, 30))
        else:
            # 如果没有图片，创建一个简单的矩形表示
            cart_img = pygame.Surface((30, 30))
            cart_img.fill((139, 69, 19))  # 棕色

        # 绘制阴影效果
        shadow_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 50))
        surface.blit(shadow_surface, (draw_x + 2, draw_y + 2))

        # 绘制小推车
        surface.blit(cart_img, (draw_x, draw_y))

        # 如果正在移动，添加一些动态效果
        if self.active and self.triggered:
            # 添加轻微的移动轨迹效果
            trail_surface = pygame.Surface((10, 30), pygame.SRCALPHA)
            trail_surface.fill((255, 255, 255, 50))
            surface.blit(trail_surface, (draw_x - 10, draw_y))

    def reset(self):
        """重置小推车到初始状态"""
        self.col = -0.5  # 重置到初始位置
        self.active = False  # 重置激活状态
        self.triggered = False  # 重置触发状态
        self.removed = False  # 重置移除状态
        self.sound_played = False  # 重置音效播放状态


class CartManager:
    """小推车管理器"""

    def __init__(self, shop_manager, images=None, sounds=None):
        self.shop_manager = shop_manager
        self.images = images
        self.sounds = sounds
        self.carts = {}  # 存储每行的小推车 {row: Cart}

        # 初始化小推车（如果已购买）
        if self.shop_manager.has_cart():
            for row in range(GRID_HEIGHT):
                self.carts[row] = Cart(row, images, sounds)

    def has_cart_in_row(self, row):
        """检查指定行是否有可用的小推车"""
        return (self.shop_manager.has_cart() and
                row in self.carts and
                not self.carts[row].triggered and
                not self.carts[row].removed)

    def trigger_cart_in_row(self, row):
        """触发指定行的小推车"""
        if self.has_cart_in_row(row):
            self.carts[row].trigger()
            return True
        return False

    def update_carts(self, zombies):
        """更新所有小推车状态"""
        hit_zombies = []

        for cart in self.carts.values():
            if cart.active and not cart.removed:
                cart_hit_zombies = cart.update(zombies)
                hit_zombies.extend(cart_hit_zombies)

        return hit_zombies

    def draw_carts(self, surface):
        """绘制所有小推车"""
        if not self.shop_manager.has_cart():
            return

        for cart in self.carts.values():
            cart.draw(surface)

    def handle_cart_click(self, x, y):
        """处理小推车点击事件"""
        if not self.shop_manager.has_cart():
            return False

        for cart in self.carts.values():
            click_rect = cart.get_click_rect()
            if click_rect and click_rect.collidepoint(x, y):
                cart.trigger()
                return True

        return False

    def check_zombie_trigger(self, zombies):
        """检查是否有僵尸触发小推车"""
        for zombie in zombies:
            if zombie.is_dying:
                continue

            # 使用僵尸中心点检查是否到达触发位置
            zombie_center_col = zombie.col + 0.3  # 僵尸中心点位置

            # 当僵尸中心点到达第一列左侧时触发小推车
            if zombie_center_col <= 0.2 and self.has_cart_in_row(zombie.row):
                self.trigger_cart_in_row(zombie.row)

    def get_save_data(self):
        """获取保存数据"""
        if not self.shop_manager.has_cart():
            return {}

        save_data = {}
        for row, cart in self.carts.items():
            save_data[row] = {
                'triggered': cart.triggered,
                'removed': cart.removed,
                'col': cart.col if cart.triggered else -0.5,
                'active': cart.active
            }
        return save_data

    def load_save_data(self, save_data):
        """从保存数据加载小推车状态"""
        if not self.shop_manager.has_cart() or not save_data:
            return

        for row, data in save_data.items():
            row = int(row)
            if row in self.carts:
                cart = self.carts[row]
                cart.triggered = data.get('triggered', False)
                cart.removed = data.get('removed', False)
                cart.col = data.get('col', -0.5)
                cart.active = data.get('active', False)

    def reset_all_carts(self):
        """重置所有小推车到初始状态"""
        if self.shop_manager.has_cart():
            for row in range(GRID_HEIGHT):
                if row in self.carts:
                    self.carts[row].reset()
                else:
                    # 如果某行没有小推车，重新创建一个
                    self.carts[row] = Cart(row, self.images, self.sounds)

    def reinitialize_carts(self):
        """重新初始化小推车（购买状态改变时调用）"""
        if self.shop_manager.has_cart():
            # 如果已购买小推车，确保每行都有小推车
            for row in range(GRID_HEIGHT):
                if row not in self.carts:
                    self.carts[row] = Cart(row, self.images, self.sounds)
                else:
                    # 重置现有小推车
                    self.carts[row].reset()
        else:
            # 如果没有购买小推车，清空所有小推车
            self.carts = {}