"""
蒲公英种子类 - 飘散攻击，自然风吹效果，击中后渐隐消失
"""
import pygame
import math
import random


class DandelionSeed:
    """蒲公英种子 - 飘散攻击，自然风吹效果，击中后渐隐消失"""

    def __init__(self, start_x, start_y, target_zombie, constants=None, images=None):
        self.start_x = start_x
        self.start_y = start_y
        self.current_x = float(start_x)
        self.current_y = float(start_y)

        self.target_zombie = target_zombie
        self.target_x = target_zombie.col if target_zombie else 5
        self.target_y = target_zombie.row if target_zombie else 2

        # 种子属性
        self.damage = 25
        self.speed = 0.024  # 较慢的移动速度
        self.life_time = 0
        self.max_life_time = 250  # 4秒生命周期

        # 风吹效果参数
        self.wind_amplitude = random.uniform(0.3, 0.5)  # 摆动幅度
        self.wind_frequency = random.uniform(0.02, 0.05)  # 摆动频率
        self.drift_speed_x = random.uniform(0.8, 1.2)  # 水平漂移速度倍数
        self.drift_speed_y = random.uniform(0.6, 1.0)  # 垂直漂移速度倍数

        # 旋转效果
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-3, 3)

        # 状态
        self.has_hit = False
        self.progress = 0.0  # 飞行进度 0-1

        # 渐隐消失效果
        self.is_fading = False  # 是否正在渐隐
        self.fade_out_timer = 0  # 渐隐计时器
        self.fade_out_duration = 90  # 渐隐持续时间（1.5秒 = 90帧）
        self.hit_slow_factor = 0.2  # 击中后的速度减缓因子

        # 存储引用
        self.constants = constants
        self.images = images

    def update(self, zombies_list=None):
        """更新种子位置和状态，支持击中后渐隐效果 - 修复：目标死亡后不再瞬移"""
        # 如果正在渐隐，只更新渐隐逻辑
        if self.is_fading:
            self.fade_out_timer += 1

            # 渐隐过程中种子继续缓慢移动
            self._update_position_during_fade()

            # 检查渐隐是否完成
            if self.fade_out_timer >= self.fade_out_duration:
                return True  # 渐隐完成，应该被移除

            return False  # 继续渐隐过程

        # 如果已击中但还未开始渐隐，开始渐隐过程
        if self.has_hit and not self.is_fading:
            self._start_fade_out()
            return False

        # 正常的生命周期检查
        self.life_time += 1
        if self.life_time >= self.max_life_time:
            return True  # 生命周期结束

        # 修复关键部分：检查目标僵尸是否还活着
        target_is_valid = (self.target_zombie and
                           self.target_zombie.health > 0 and
                           zombies_list and self.target_zombie in zombies_list)

        # 如果目标无效，不再重新寻找目标，而是继续按当前方向飞行
        if not target_is_valid:
            # 目标已死亡或无效，保持当前目标位置不变
            # 种子将继续朝着最后已知的目标位置飞行
            pass  # 不做任何重定向操作
        else:
            # 如果目标仍然有效，更新目标位置
            if self.target_zombie:
                self.target_x = self.target_zombie.col
                self.target_y = self.target_zombie.row

        # 正常的移动逻辑
        self._update_normal_movement()

        return False

    def _start_fade_out(self):
        """开始渐隐过程"""
        self.is_fading = True
        self.fade_out_timer = 0

        # 可选：播放击中音效（如果有的话）
        # if self.sounds and self.sounds.get("seed_hit"):
        #     self.sounds["seed_hit"].play()

    def _update_position_during_fade(self):
        """渐隐过程中的位置更新（速度减缓）"""
        # 计算减缓后的移动
        dx = self.target_x - self.start_x
        dy = self.target_y - self.start_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0.1:
            # 使用减缓的速度继续移动
            reduced_speed = self.speed * self.hit_slow_factor
            self.progress += reduced_speed
            self.progress = min(1.0, self.progress)

            # 基础直线插值
            base_x = self.start_x + dx * self.progress * self.drift_speed_x
            base_y = self.start_y + dy * self.progress * self.drift_speed_y

            # 减弱的风吹摆动效果
            fade_factor = 1.0 - (self.fade_out_timer / self.fade_out_duration)
            wind_offset_x = math.sin(self.life_time * self.wind_frequency) * self.wind_amplitude * fade_factor * 0.5
            wind_offset_y = math.cos(
                self.life_time * self.wind_frequency * 0.7) * self.wind_amplitude * fade_factor * 0.3

            # 减弱的随机微风扰动
            micro_wind_x = math.sin(self.life_time * 0.1) * 0.05 * fade_factor
            micro_wind_y = math.cos(self.life_time * 0.08) * 0.04 * fade_factor

            # 最终位置
            self.current_x = base_x + wind_offset_x + micro_wind_x
            self.current_y = base_y + wind_offset_y + micro_wind_y

            # 减缓旋转速度
            self.rotation += self.rotation_speed * fade_factor * 0.5

    def _update_normal_movement(self):
        """正常的移动逻辑 - 修改：即使目标死亡也继续朝目标位置飞行"""
        # 计算基础方向（朝最后已知的目标位置）
        dx = self.target_x - self.start_x
        dy = self.target_y - self.start_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0.1:
            # 更新飞行进度
            self.progress += self.speed
            self.progress = min(1.0, self.progress)

            # 基础直线插值（朝最后已知目标位置）
            base_x = self.start_x + dx * self.progress * self.drift_speed_x
            base_y = self.start_y + dy * self.progress * self.drift_speed_y

            # 添加风吹摆动效果
            wind_offset_x = math.sin(self.life_time * self.wind_frequency) * self.wind_amplitude
            wind_offset_y = math.cos(self.life_time * self.wind_frequency * 0.7) * self.wind_amplitude * 0.5

            # 添加随机微风扰动
            micro_wind_x = math.sin(self.life_time * 0.1) * 0.1
            micro_wind_y = math.cos(self.life_time * 0.08) * 0.08

            # 最终位置
            self.current_x = base_x + wind_offset_x + micro_wind_x
            self.current_y = base_y + wind_offset_y + micro_wind_y

            # 更新旋转
            self.rotation += self.rotation_speed
        else:
            # 如果已经到达目标位置，种子应该停止移动或开始消散
            # 这里可以设置种子开始渐隐或其他结束行为
            pass

    def can_hit_zombie(self, zombie):
        """检查是否可以击中僵尸"""
        if self.has_hit or zombie.health <= 0 or self.is_fading:
            return False

        # 检查距离
        distance = math.sqrt((zombie.col - self.current_x) ** 2 +
                             (zombie.row - self.current_y) ** 2)
        return distance < 0.4

    def attack_zombie(self, zombie):
        """攻击僵尸 - 修改：只有当僵尸血量确实降低时才开始渐隐动画"""
        if self.has_hit or zombie.health <= 0 or self.is_fading:
            return False

        if self.can_hit_zombie(zombie):
            # 记录攻击前的总血量（生命值 + 护甲值）
            old_total_health = zombie.health + (zombie.armor_health if zombie.has_armor else 0)

            # 造成伤害
            if zombie.has_armor and zombie.armor_health > 0:
                zombie.armor_health -= self.damage
                if zombie.armor_health < 0:
                    zombie.health += zombie.armor_health  # 剩余伤害转到生命值
                    zombie.armor_health = 0
            else:
                zombie.health -= self.damage

            zombie.health = max(0, zombie.health)

            # 记录攻击后的总血量
            new_total_health = zombie.health + (zombie.armor_health if zombie.has_armor else 0)

            # 关键修改：只有当僵尸的血量确实降低时，才设置为已击中并开始渐隐动画
            damage_actually_dealt = old_total_health > new_total_health
            if damage_actually_dealt:
                self.has_hit = True

            # 检查僵尸是否需要开始死亡动画
            if zombie.health <= 0 and not zombie.is_dying:
                zombie.start_death_animation()

            return damage_actually_dealt  # 返回是否真正造成了伤害

        return False

    def get_display_position(self):
        """获取显示位置"""
        return self.current_x, self.current_y, 0

    def get_current_alpha(self):
        """获取当前透明度（用于渐隐效果）"""
        if not self.is_fading:
            # 根据生命周期计算透明度
            life_ratio = 1.0 - (self.life_time / self.max_life_time)
            return int(255 * life_ratio)
        else:
            # 渐隐过程中的透明度
            fade_progress = self.fade_out_timer / self.fade_out_duration
            base_alpha = 255 * (1.0 - (self.life_time / self.max_life_time))
            fade_alpha = base_alpha * (1.0 - fade_progress)
            return int(max(0, fade_alpha))

    def draw(self, surface):
        """绘制蒲公英种子，支持渐隐效果"""
        if not self.constants:
            return

        # 计算屏幕坐标
        x = (self.constants['BATTLEFIELD_LEFT'] +
             self.current_x * (self.constants['GRID_SIZE'] + self.constants['GRID_GAP']))
        y = (self.constants['BATTLEFIELD_TOP'] +
             self.current_y * (self.constants['GRID_SIZE'] + self.constants['GRID_GAP']) +
             self.constants['GRID_SIZE'] // 2)

        # 计算当前透明度
        alpha = self.get_current_alpha()

        # 如果透明度太低，不绘制
        if alpha < 10:
            return

        if self.images and self.images.get('dandelion_seed_img'):
            # 使用种子图片
            seed_img = self.images['dandelion_seed_img']

            # 旋转图片
            if abs(self.rotation) > 0.1:
                rotated_img = pygame.transform.rotate(seed_img, self.rotation)
            else:
                rotated_img = seed_img

            # 应用透明度
            rotated_img = rotated_img.copy()
            rotated_img.set_alpha(alpha)

            # 绘制种子
            rect = rotated_img.get_rect(center=(int(x), int(y)))
            surface.blit(rotated_img, rect)
        else:
            # 默认绘制：白色小圆点带尾迹
            # 主体种子
            pygame.draw.circle(surface, (255, 255, 255, alpha), (int(x), int(y)), 3)

            # 绘制飘散尾迹（渐隐时减弱）
            trail_length = 5 if not self.is_fading else 3
            trail_intensity = 1.0 if not self.is_fading else 0.5

            for i in range(trail_length):
                trail_ratio = (i + 1) / trail_length
                trail_alpha = int(alpha * (1 - trail_ratio) * 0.5 * trail_intensity)
                trail_x = x - self.wind_amplitude * trail_ratio * 10
                trail_y = y - trail_ratio * 2

                if trail_alpha > 10:
                    trail_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surface, (255, 255, 200, trail_alpha), (3, 3), 2)
                    surface.blit(trail_surface, (int(trail_x - 3), int(trail_y - 3)))