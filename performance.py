"""
性能监控模块
"""
import pygame


class PerformanceMonitor:
    """监控游戏性能，动态调整视觉效果"""

    def __init__(self):
        self.frame_times = []
        self.max_samples = 60
        self.last_time = pygame.time.get_ticks()

    def update(self):
        """更新性能监控数据"""
        current_time = pygame.time.get_ticks()
        dt = current_time - self.last_time
        self.last_time = current_time

        self.frame_times.append(dt)
        if len(self.frame_times) > self.max_samples:
            self.frame_times.pop(0)

    def get_avg_fps(self):
        """获取平均FPS"""
        if not self.frame_times:
            return 60
        avg_time = sum(self.frame_times) / len(self.frame_times)
        return 1000 / avg_time if avg_time > 0 else 60

    def should_reduce_effects(self):
        """检查是否应该减少特效（低性能模式）"""
        avg_fps = self.get_avg_fps()
        return avg_fps < 30

    def is_lagging(self):
        """检查是否存在卡顿（中等性能模式）"""
        avg_fps = self.get_avg_fps()
        return avg_fps < 45


class SpatialGrid:
    """简单的空间分区系统，减少不必要的碰撞检测"""

    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.reset()

    def reset(self):
        """重置网格，清空所有单元格"""
        self.cells = [[[] for _ in range(self.grid_width)] for _ in range(self.grid_height)]

    def add_zombie(self, zombie):
        """将僵尸添加到对应的网格单元格中"""
        row = int(zombie.row)
        col = int(min(max(zombie.col, 0), self.grid_width - 1))  # 确保列索引在有效范围内
        if 0 <= row < self.grid_height:
            self.cells[row][col].append(zombie)

    def get_zombies_in_row(self, row):
        """只返回指定行的僵尸，大大减少检测范围"""
        if 0 <= row < self.grid_height:
            zombies_in_row = []
            for col in range(self.grid_width):
                zombies_in_row.extend(self.cells[row][col])
            return zombies_in_row
        return []