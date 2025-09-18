"""
性能监控模块
"""
import pygame
import time
from collections import deque
import gc


class PerformanceMonitor:
    """高级性能监控器，提供多级性能调整和智能优化"""

    def __init__(self):
        # 使用deque提高性能
        self.frame_times = deque(maxlen=120)  # 存储2秒的帧时间数据
        self.short_frame_times = deque(maxlen=30)  # 存储0.5秒的短期数据

        # 时间测量
        self.last_time = time.perf_counter()
        self.target_fps = 60
        self.min_frame_time = 1.0 / self.target_fps

        # 性能等级
        self.performance_level = 3  # 0=最低, 1=低, 2=中, 3=高, 4=最高
        self.last_performance_check = 0
        self.performance_check_interval = 60  # 每秒检查一次

        # 智能调整参数
        self.consecutive_low_fps = 0
        self.consecutive_good_fps = 0
        self.adjustment_threshold = 30  # 30帧连续低性能才调整

        # 内存监控
        self.last_gc_time = time.perf_counter()
        self.gc_interval = 5.0  # 5秒强制GC一次

        # 性能统计
        self.total_frames = 0
        self.dropped_frames = 0

        # 预计算的阈值
        self.fps_thresholds = {
            'excellent': 55,
            'good': 45,
            'acceptable': 35,
            'poor': 25,
            'critical': 15
        }

    def should_reduce_zombie_death_effects(self):
        """是否应该减少僵尸死亡效果"""
        return self.performance_level <= 2 or self.is_lagging()

    def update(self):
        """高效的性能监控更新"""
        current_time = time.perf_counter()
        dt = current_time - self.last_time
        self.last_time = current_time

        # 添加到队列
        self.frame_times.append(dt)
        self.short_frame_times.append(dt)
        self.total_frames += 1

        # 检测掉帧
        if dt > self.min_frame_time * 1.5:
            self.dropped_frames += 1

        # 定期性能评估和调整
        if self.total_frames % self.performance_check_interval == 0:
            self._evaluate_and_adjust_performance()

        # 智能垃圾回收
        if current_time - self.last_gc_time > self.gc_interval:
            self._smart_garbage_collection()
            self.last_gc_time = current_time

    def _evaluate_and_adjust_performance(self):
        """评估性能并自动调整"""
        current_fps = self.get_avg_fps()
        short_fps = self.get_short_term_fps()

        # 基于短期和长期FPS判断性能趋势
        if short_fps < self.fps_thresholds['poor']:
            self.consecutive_low_fps += 1
            self.consecutive_good_fps = 0
        elif short_fps > self.fps_thresholds['good']:
            self.consecutive_good_fps += 1
            self.consecutive_low_fps = 0
        else:
            self.consecutive_low_fps = max(0, self.consecutive_low_fps - 1)
            self.consecutive_good_fps = max(0, self.consecutive_good_fps - 1)

        # 自动调整性能等级
        if self.consecutive_low_fps >= self.adjustment_threshold:
            self.performance_level = max(0, self.performance_level - 1)
            self.consecutive_low_fps = 0
        elif self.consecutive_good_fps >= self.adjustment_threshold * 2:
            self.performance_level = min(4, self.performance_level + 1)
            self.consecutive_good_fps = 0

    def _smart_garbage_collection(self):
        """智能垃圾回收，避免卡顿"""
        # 只在性能充足时进行完整GC
        if self.get_short_term_fps() > self.fps_thresholds['good']:
            gc.collect()
        else:
            # 性能不足时只进行轻量级清理
            gc.collect(0)

    def get_avg_fps(self):
        """获取长期平均FPS"""
        if not self.frame_times:
            return self.target_fps

        avg_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_time if avg_time > 0 else self.target_fps

    def get_short_term_fps(self):
        """获取短期平均FPS（更敏感）"""
        if not self.short_frame_times:
            return self.target_fps

        avg_time = sum(self.short_frame_times) / len(self.short_frame_times)
        return 1.0 / avg_time if avg_time > 0 else self.target_fps

    def should_reduce_effects(self):
        """是否应该减少特效"""
        return self.performance_level <= 1

    def should_reduce_particles(self):
        """是否应该减少粒子效果"""
        return self.performance_level <= 2

    def should_reduce_animations(self):
        """是否应该减少动画"""
        return self.performance_level <= 1

    def should_skip_frame_updates(self):
        """是否应该跳过某些帧更新"""
        return self.performance_level == 0

    def is_lagging(self):
        """检查是否存在卡顿"""
        return self.get_short_term_fps() < self.fps_thresholds['acceptable']

    def is_critical_performance(self):
        """检查是否处于严重性能问题状态"""
        return self.get_short_term_fps() < self.fps_thresholds['critical']

    def get_performance_stats(self):
        """获取性能统计信息"""
        if self.total_frames == 0:
            return {}

        return {
            'current_fps': self.get_short_term_fps(),
            'average_fps': self.get_avg_fps(),
            'performance_level': self.performance_level,
            'dropped_frame_rate': self.dropped_frames / self.total_frames,
            'total_frames': self.total_frames
        }

    def get_update_interval(self):
        """根据性能等级返回更新间隔"""
        intervals = {0: 3, 1: 2, 2: 1, 3: 1, 4: 1}
        return intervals.get(self.performance_level, 1)


class SpatialGrid:
    """高性能空间分区系统"""

    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height

        # 预分配内存，避免动态分配
        self.cells = []
        self.zombie_positions = {}  # 缓存僵尸位置
        self.dirty_rows = set()  # 标记需要更新的行

        # 对象池
        self.list_pool = deque(maxlen=50)  # 重用列表对象
        self.reset()

    def reset(self):
        """高效重置网格"""
        # 回收旧的列表到对象池
        for row in self.cells:
            for cell_list in row:
                if cell_list:
                    cell_list.clear()
                    if len(self.list_pool) < self.list_pool.maxlen:
                        self.list_pool.append(cell_list)

        # 重新初始化网格
        self.cells = [[self._get_list() for _ in range(self.grid_width)]
                      for _ in range(self.grid_height)]
        self.zombie_positions.clear()
        self.dirty_rows.clear()

    def _get_list(self):
        """从对象池获取列表或创建新列表"""
        if self.list_pool:
            return self.list_pool.popleft()
        return []

    def add_zombie(self, zombie):
        """高效添加僵尸到网格"""
        zombie_id = id(zombie)

        # 检查僵尸是否已经在网格中
        if zombie_id in self.zombie_positions:
            old_row, old_col = self.zombie_positions[zombie_id]
            # 如果位置没变，直接返回
            new_row = int(zombie.row)
            new_col = int(min(max(zombie.col, 0), self.grid_width - 1))
            if old_row == new_row and old_col == new_col:
                return

            # 从旧位置移除
            if (0 <= old_row < self.grid_height and
                    0 <= old_col < self.grid_width):
                try:
                    self.cells[old_row][old_col].remove(zombie)
                except ValueError:
                    pass  # 僵尸可能已经被移除

        # 添加到新位置
        row = int(zombie.row)
        col = int(min(max(zombie.col, 0), self.grid_width - 1))

        if 0 <= row < self.grid_height:
            self.cells[row][col].append(zombie)
            self.zombie_positions[zombie_id] = (row, col)
            self.dirty_rows.add(row)

    def remove_zombie(self, zombie):
        """从网格中移除僵尸"""
        zombie_id = id(zombie)
        if zombie_id in self.zombie_positions:
            row, col = self.zombie_positions[zombie_id]
            if (0 <= row < self.grid_height and
                    0 <= col < self.grid_width):
                try:
                    self.cells[row][col].remove(zombie)
                    self.dirty_rows.add(row)
                except ValueError:
                    pass
            del self.zombie_positions[zombie_id]

    def get_zombies_in_row(self, row):
        """高效获取指定行的僵尸"""
        if not (0 <= row < self.grid_height):
            return []

        # 使用生成器表达式减少内存分配
        zombies = []
        for col in range(self.grid_width):
            zombies.extend(self.cells[row][col])
        return zombies

    def get_zombies_in_area(self, start_row, end_row, start_col, end_col):
        """获取指定区域的僵尸"""
        zombies = []
        for row in range(max(0, start_row), min(self.grid_height, end_row + 1)):
            for col in range(max(0, start_col), min(self.grid_width, end_col + 1)):
                zombies.extend(self.cells[row][col])
        return zombies

    def get_zombie_count(self):
        """获取总僵尸数量"""
        return len(self.zombie_positions)

    def cleanup_dead_zombies(self, alive_zombies):
        """清理已死亡的僵尸引用"""
        alive_ids = {id(zombie) for zombie in alive_zombies}
        dead_ids = set(self.zombie_positions.keys()) - alive_ids

        for zombie_id in dead_ids:
            if zombie_id in self.zombie_positions:
                row, col = self.zombie_positions[zombie_id]
                # 从网格中查找并移除死亡僵尸
                if (0 <= row < self.grid_height and
                        0 <= col < self.grid_width):
                    cell = self.cells[row][col]
                    self.cells[row][col] = [z for z in cell if id(z) in alive_ids]
                    if len(self.cells[row][col]) != len(cell):
                        self.dirty_rows.add(row)
                del self.zombie_positions[zombie_id]


class ObjectPool:
    """通用对象池，减少对象创建和销毁的开销"""

    def __init__(self, create_func, reset_func=None, max_size=100):
        self.create_func = create_func
        self.reset_func = reset_func
        self.pool = deque(maxlen=max_size)
        self.active_objects = set()

    def get_object(self):
        """从对象池获取对象"""
        if self.pool:
            obj = self.pool.popleft()
            if self.reset_func:
                self.reset_func(obj)
        else:
            obj = self.create_func()

        self.active_objects.add(id(obj))
        return obj

    def return_object(self, obj):
        """将对象返回到对象池"""
        obj_id = id(obj)
        if obj_id in self.active_objects:
            self.active_objects.remove(obj_id)
            if len(self.pool) < self.pool.maxlen:
                self.pool.append(obj)

    def cleanup(self):
        """清理对象池"""
        self.pool.clear()
        self.active_objects.clear()


class BatchProcessor:
    """批量处理器，减少频繁的单个更新操作"""

    def __init__(self, batch_size=50):
        self.batch_size = batch_size
        self.pending_updates = deque()
        self.last_process_time = time.perf_counter()
        self.process_interval = 1.0 / 60  # 每帧处理一次

    def add_update(self, update_func, *args, **kwargs):
        """添加待处理的更新"""
        self.pending_updates.append((update_func, args, kwargs))

    def process_batch(self, force=False):
        """处理批量更新"""
        current_time = time.perf_counter()

        if not force and current_time - self.last_process_time < self.process_interval:
            return

        processed = 0
        while self.pending_updates and processed < self.batch_size:
            update_func, args, kwargs = self.pending_updates.popleft()
            try:
                update_func(*args, **kwargs)
            except Exception:
                pass  # 忽略处理错误，避免整个批处理失败
            processed += 1

        self.last_process_time = current_time

    def has_pending_updates(self):
        """检查是否有待处理的更新"""
        return len(self.pending_updates) > 0


class FrameSkipper:
    """智能帧跳跃器，在性能不足时跳过某些更新"""

    def __init__(self):
        self.frame_counter = 0
        self.skip_patterns = {
            0: lambda x: False,  # 不跳过
            1: lambda x: x % 2 == 1,  # 跳过奇数帧
            2: lambda x: x % 3 != 0,  # 每3帧只更新1帧
            3: lambda x: x % 4 != 0,  # 每4帧只更新1帧
            4: lambda x: x % 5 != 0,  # 每5帧只更新1帧
        }

    def should_skip_update(self, performance_level, update_type='normal'):
        """根据性能等级判断是否跳过更新"""
        self.frame_counter += 1

        # 重要更新（如输入处理）永不跳过
        if update_type == 'critical':
            return False

        # 根据性能等级选择跳帧模式
        skip_func = self.skip_patterns.get(4 - performance_level, self.skip_patterns[0])
        return skip_func(self.frame_counter)

    def reset_counter(self):
        """重置帧计数器"""
        self.frame_counter = 0