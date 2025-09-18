"""
射击型植物基类
"""
import random
from .base_plant import BasePlant


class ShooterPlant(BasePlant):
    """射击型植物的基类"""

    def __init__(self, row, col, plant_type, constants, images, level_manager, base_shoot_delay=60):
        super().__init__(row, col, plant_type, constants, images, level_manager)

        # 射击参数
        self.base_shoot_delay = base_shoot_delay

        # 当前实际使用的射击间隔（带随机波动和关卡加成）
        self.current_shoot_delay = self._calculate_random_delay()

        # 设置随机初始值，避免所有植物同时攻击
        self.shoot_timer = random.randint(0, self.current_shoot_delay)

        # 用于检测新僵尸波次的变量
        self.had_target_last_frame = False

    def _calculate_random_delay(self):
        """计算带有随机波动和关卡加成的射击间隔"""
        if self.plant_type not in ["shooter", "melon_pult", "cattail", "dandelion", "lightning_flower", "ice_cactus"]:
            return self.base_shoot_delay

        # 获取关卡射速倍率
        speed_multiplier = 1.0
        if self.level_manager and self.level_manager.has_plant_speed_boost():
            speed_multiplier = self.level_manager.get_plant_speed_multiplier()

        # 应用射速倍率（倍率越高，间隔越短）
        adjusted_delay = int(self.base_shoot_delay / speed_multiplier)

        # 根据植物类型设置不同的波动范围
        variation_percent = self._get_variation_percent()
        variation = int(adjusted_delay * variation_percent)

        return adjusted_delay + random.randint(-variation, variation)

    def _get_variation_percent(self):
        """获取射击间隔的波动百分比"""
        if self.plant_type == "cattail":
            return 0.05  # ±5%
        elif self.plant_type in ["melon_pult", "dandelion", "lightning_flower", "ice_cactus"]:
            return 0.08  # ±8%
        else:  # shooter
            return 0.1  # ±10%

    def update(self):
        """更新射击计时器"""
        # 速度倍率支持
        speed_multiplier = 1.0
        if self.level_manager and self.level_manager.has_plant_speed_boost():
            speed_multiplier = self.level_manager.get_plant_speed_multiplier()

        # 速度倍率越高，计时器增加越快
        self.shoot_timer += speed_multiplier
        return 0

    def check_for_new_wave(self, has_target_now):
        """检测是否有新僵尸波次出现，并添加随机延时"""
        # 如果之前没有目标，现在有了目标，说明新一波僵尸出现
        if not self.had_target_last_frame and has_target_now:
            current_base_delay = self._get_current_base_delay()

            # 添加0-15%的随机延时
            max_delay = int(current_base_delay * 0.15)
            extra_delay = random.randint(0, max_delay)

            if self.shoot_timer >= self.current_shoot_delay:
                self.shoot_timer = self.current_shoot_delay - extra_delay

        self.had_target_last_frame = has_target_now

    def _get_current_base_delay(self):
        """获取当前的基础射击间隔（考虑关卡加成）"""
        if self.level_manager and self.level_manager.has_special_feature('plant_speed_boost'):
            speed_multiplier = self.level_manager.get_plant_speed_multiplier()
            return int(self.base_shoot_delay / speed_multiplier)
        return self.base_shoot_delay

    def can_shoot(self):
        """检查是否可以射击"""
        return self.shoot_timer >= self.current_shoot_delay

    def reset_shoot_timer(self):
        """重置射击计时器并重新计算随机射击间隔"""
        self.shoot_timer = 0
        self.current_shoot_delay = self._calculate_random_delay()