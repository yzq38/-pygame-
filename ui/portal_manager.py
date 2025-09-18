"""
传送门管理器模块 - 管理传送门的生成、移动和动画效果
"""
import pygame
import random
import math
from typing import List, Tuple, Optional
from core.constants import *


class Portal:
    """传送门类"""

    def __init__(self, row: int, col: int, portal_id: int):
        self.row = row
        self.col = col
        self.portal_id = portal_id

        # 动画相关
        self.spawn_animation_timer = 0
        self.despawn_animation_timer = 0
        self.is_spawning = True
        self.is_despawning = False
        self.is_active = False

        # 动画持续时间（帧数）
        self.spawn_duration = 60  # 1秒出现动画
        self.despawn_duration = 30  # 0.5秒消失动画

        # 视觉效果
        self.rotation_angle = 0

        # 粒子效果
        self.particles = []
        self.particle_timer = 0

    def update(self):
        """更新传送门状态和动画"""
        # 更新旋转角度
        self.rotation_angle += 2
        if self.rotation_angle >= 360:
            self.rotation_angle = 0

        # 更新出现动画
        if self.is_spawning:
            self.spawn_animation_timer += 1
            if self.spawn_animation_timer >= self.spawn_duration:
                self.is_spawning = False
                self.is_active = True

        # 更新消失动画
        if self.is_despawning:
            self.despawn_animation_timer += 1
            if self.despawn_animation_timer >= self.despawn_duration:
                return True  # 标记为需要移除

        # 更新粒子效果
        self.update_particles()

        return False

    def update_particles(self):
        """更新粒子效果 - 减少粒子数量"""
        # 生成新粒子 - 降低生成频率从每3帧到每8帧
        self.particle_timer += 1
        if self.particle_timer % 8 == 0 and self.is_active:
            self.create_particle()

        # 更新现有粒子
        for particle in self.particles[:]:
            particle['life'] -= 1
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            particle['alpha'] = max(0, particle['alpha'] - 2)  # 减慢透明度衰减

            if particle['life'] <= 0 or particle['alpha'] <= 0:
                self.particles.remove(particle)

    def create_particle(self):
        """创建科技感粒子 - 减少数量"""
        center_x = BATTLEFIELD_LEFT + self.col * (GRID_SIZE + GRID_GAP) + GRID_SIZE // 2
        center_y = BATTLEFIELD_TOP + self.row * (GRID_SIZE + GRID_GAP) + GRID_SIZE // 2

        # 创建环形粒子 - 减少半径范围
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(15, 25)  # 缩小半径范围

        particle = {
            'x': center_x + math.cos(angle) * radius,
            'y': center_y + math.sin(angle) * radius,
            'vel_x': math.cos(angle) * 0.3,  # 降低速度
            'vel_y': math.sin(angle) * 0.3,
            'life': 45,  # 减少生命周期
            'alpha': 200,  # 降低初始透明度，减少透明感
            'color': random.choice([(0, 255, 255), (0, 200, 255), (100, 255, 255)])
        }

        self.particles.append(particle)

    def start_despawn(self):
        """开始消失动画"""
        self.is_despawning = True
        self.is_active = False
        self.despawn_animation_timer = 0

    def get_screen_pos(self):
        """获取屏幕坐标"""
        x = BATTLEFIELD_LEFT + self.col * (GRID_SIZE + GRID_GAP)
        y = BATTLEFIELD_TOP + self.row * (GRID_SIZE + GRID_GAP)
        return x, y

    def get_center_pos(self):
        """获取中心坐标"""
        x, y = self.get_screen_pos()
        return x + GRID_SIZE // 2, y + GRID_SIZE // 2

    def draw(self, surface):
        """绘制传送门"""
        center_x, center_y = self.get_center_pos()

        # 计算动画进度
        if self.is_spawning:
            progress = self.spawn_animation_timer / self.spawn_duration
            alpha_multiplier = progress
            scale = progress
        elif self.is_despawning:
            progress = self.despawn_animation_timer / self.despawn_duration
            alpha_multiplier = 1.0 - progress
            scale = 1.0 - progress * 0.3
        else:
            alpha_multiplier = 1.0
            scale = 1.0  # 移除脉冲效果，保持固定大小

        # 绘制外环 - 降低透明度
        outer_radius = int(35 * scale)
        outer_alpha = int(180 * alpha_multiplier)  # 提高透明度，从100到180
        if outer_alpha > 0:
            outer_surface = pygame.Surface((outer_radius * 2, outer_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(outer_surface, (0, 255, 255, outer_alpha),
                               (outer_radius, outer_radius), outer_radius, 3)
            surface.blit(outer_surface, (center_x - outer_radius, center_y - outer_radius))

        # 绘制内环（旋转）- 降低透明度
        inner_radius = int(25 * scale)
        inner_alpha = int(25 * alpha_multiplier)
        if inner_alpha > 0:
            # 创建旋转的内环
            inner_surface = pygame.Surface((inner_radius * 2, inner_radius * 2), pygame.SRCALPHA)

            # 绘制多个弧段创造旋转效果
            for i in range(6):
                start_angle = math.radians(self.rotation_angle + i * 60)
                end_angle = math.radians(self.rotation_angle + i * 60 + 30)

                # 计算弧段的点
                points = []
                for angle in [start_angle, end_angle]:
                    x = inner_radius + inner_radius * 0.8 * math.cos(angle)
                    y = inner_radius + inner_radius * 0.8 * math.sin(angle)
                    points.append((x, y))

                if len(points) >= 2:
                    pygame.draw.line(inner_surface, (100, 255, 255, inner_alpha),
                                     points[0], points[1], 2)

            surface.blit(inner_surface, (center_x - inner_radius, center_y - inner_radius))

        # 绘制中心椭圆光点 - 改为竖直椭圆
        core_alpha = int(255 * alpha_multiplier)
        if core_alpha > 0:
            ellipse_width = int(22 * scale)  # 椭圆宽度
            ellipse_height = int(36 * scale)  # 椭圆高度，比宽度大

            # 创建椭圆surface
            ellipse_surface = pygame.Surface((ellipse_width, ellipse_height), pygame.SRCALPHA)

            # 绘制椭圆
            ellipse_rect = pygame.Rect(0, 0, ellipse_width, ellipse_height)
            pygame.draw.ellipse(ellipse_surface, (255, 255, 255, core_alpha), ellipse_rect)

            # 绘制到主surface，居中对齐
            surface.blit(ellipse_surface,
                         (center_x - ellipse_width // 2, center_y - ellipse_height // 2))

        # 绘制粒子效果
        self.draw_particles(surface)

    def draw_particles(self, surface):
        """绘制粒子效果"""
        for particle in self.particles:
            if particle['alpha'] > 0:
                particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                color = (*particle['color'], int(particle['alpha']))
                pygame.draw.circle(particle_surface, color, (2, 2), 2)
                surface.blit(particle_surface, (int(particle['x']) - 2, int(particle['y']) - 2))


class PortalManager:
    """传送门管理器 - 修复版本"""

    def __init__(self, level_manager, auto_initialize=True):
        self.level_manager = level_manager
        self.portals: List[Portal] = []
        self.switch_timer = 0
        self.switch_interval = 20 * 60  # 20秒 = 1200帧

        # 安全的列位置设置 - 确保在战场范围内
        grid_width = GRID_WIDTH if 'GRID_WIDTH' in globals() else 9

        self.right_cols = [4,5, 6,7,8]

        self.next_portal_id = 0

        # 标记是否正在从保存数据恢复
        self._is_restoring = False

        # 只有在需要时才初始化传送门
        if auto_initialize:
            self.initialize_portals()

    def initialize_portals(self):
        """初始化两个传送门"""
        # 如果正在恢复，跳过自动初始化
        if self._is_restoring:
            return

        # 清空现有传送门
        self.portals.clear()

        # 随机选择两个不同的行
        available_rows = list(range(GRID_HEIGHT))
        selected_rows = random.sample(available_rows, 2)

        # 为每个行随机选择列
        for row in selected_rows:
            col = random.choice(self.right_cols)
            portal = Portal(row, col, self.next_portal_id)
            self.portals.append(portal)
            self.next_portal_id += 1

    def start_restore_mode(self):
        """开始恢复模式"""
        self._is_restoring = True
        self.portals.clear()  # 清空所有传送门

    def finish_restore_mode(self):
        """结束恢复模式"""
        self._is_restoring = False

    def add_restored_portal(self, portal_data):
        """添加从保存数据恢复的传送门"""
        if not self._is_restoring:
            print("警告：不在恢复模式下调用 add_restored_portal")
            return

        portal = Portal(portal_data["row"], portal_data["col"], portal_data["portal_id"])

        # 恢复传送门的详细状态
        portal.spawn_animation_timer = portal_data.get("spawn_animation_timer", 60)
        portal.despawn_animation_timer = portal_data.get("despawn_animation_timer", 0)
        portal.is_spawning = portal_data.get("is_spawning", False)
        portal.is_despawning = portal_data.get("is_despawning", False)
        portal.is_active = portal_data.get("is_active", True)
        portal.rotation_angle = portal_data.get("rotation_angle", 0)

        self.portals.append(portal)

        # 更新next_portal_id以避免ID冲突
        self.next_portal_id = max(self.next_portal_id, portal_data["portal_id"] + 1)

    def update(self):
        """更新传送门管理器"""
        # 如果正在恢复，暂停所有更新逻辑
        if self._is_restoring:
            return

        # 更新现有传送门
        for portal in self.portals[:]:
            should_remove = portal.update()
            if should_remove:
                self.portals.remove(portal)

        # 更新切换计时器
        self.switch_timer += 1
        if self.switch_timer >= self.switch_interval:
            self.switch_random_portal()
            self.switch_timer = 0

    def switch_random_portal(self):
        """随机切换一个传送门的位置"""
        # 如果正在恢复，跳过切换
        if self._is_restoring:
            return

        if len(self.portals) < 2:
            return

        # 选择一个活跃的传送门进行切换
        active_portals = [p for p in self.portals if p.is_active]
        if not active_portals:
            return

        portal_to_switch = random.choice(active_portals)

        # 获取当前占用的行
        occupied_rows = [p.row for p in self.portals if p != portal_to_switch]

        # 选择新位置
        available_rows = [row for row in range(GRID_HEIGHT) if row not in occupied_rows]
        if not available_rows:
            return

        new_row = random.choice(available_rows)
        new_col = random.choice(self.right_cols)

        # 开始旧传送门的消失动画
        portal_to_switch.start_despawn()

        # 创建新传送门
        new_portal = Portal(new_row, new_col, self.next_portal_id)
        self.portals.append(new_portal)
        self.next_portal_id += 1

    # ... 其他方法保持不变 ...
    def get_portal_at_position(self, row: int, col: int) -> Optional[Portal]:
        """获取指定位置的传送门"""
        for portal in self.portals:
            if portal.row == row and portal.col == col and portal.is_active:
                return portal
        return None

    def can_place_plant_at(self, row: int, col: int) -> bool:
        """检查指定位置是否可以放置植物（不被传送门占用）"""
        return self.get_portal_at_position(row, col) is None

    def draw_portals(self, surface):
        """绘制所有传送门"""
        for portal in self.portals:
            portal.draw(surface)

    def teleport_zombie(self, zombie):
        """传送僵尸到另一个传送门"""
        if len(self.portals) < 2:
            return False

        # 找到僵尸当前所在的传送门
        current_portal = None
        for portal in self.portals:
            if (portal.is_active and
                    abs(zombie.row - portal.row) < 0.5 and
                    abs(zombie.col - portal.col) < 0.5):
                current_portal = portal
                break

        if not current_portal:
            return False

        # 找到另一个活跃的传送门
        other_portals = [p for p in self.portals if p.is_active and p != current_portal]
        if not other_portals:
            return False

        target_portal = random.choice(other_portals)

        # 传送僵尸
        zombie.row = target_portal.row
        zombie.col = target_portal.col

        # 可以添加传送特效
        self.create_teleport_effect(current_portal, target_portal)

        return True

    def create_teleport_effect(self, from_portal: Portal, to_portal: Portal):
        """创建传送特效 - 减少粒子数量"""
        # 在两个传送门之间创建额外的粒子效果，减少数量
        for _ in range(10):  # 从20减少到10
            from_portal.create_particle()
            to_portal.create_particle()

    def is_portal_system_active(self) -> bool:
        """检查传送门系统是否激活"""
        return len([p for p in self.portals if p.is_active]) >= 2