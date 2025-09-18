"""
植物飞行动画 - 处理植物选择界面的飞行动画效果
"""
import math
import pygame
from .constants import PLANT_FLYING_DURATION, PLANT_FLYING_ARC_HEIGHT
from .effects import AnimationEffects


class PlantFlyingAnimation:
    """植物飞行动画类 - 支持正向和反向动画"""

    def __init__(self, plant_type, start_pos, target_pos, plant_data, reverse=False):
        self.plant_type = plant_type
        self.start_pos = start_pos
        self.target_pos = target_pos
        self.plant_data = plant_data
        self.reverse = reverse

        # 动画参数
        self.duration = PLANT_FLYING_DURATION
        self.timer = 0
        self.completed = False

        # 当前位置
        self.current_pos = list(start_pos)

        # 弧形飞行参数
        self.mid_height = PLANT_FLYING_ARC_HEIGHT if not reverse else -PLANT_FLYING_ARC_HEIGHT

        # 缓动函数
        self.effects = AnimationEffects()

    def update(self):
        """更新飞行动画"""
        if self.completed:
            return

        self.timer += 1
        progress = min(1.0, self.timer / self.duration)

        # 选择缓动函数
        if self.reverse:
            eased_progress = self.effects.ease_in_cubic(progress)
        else:
            eased_progress = self.effects.ease_out_cubic(progress)

        # 计算当前位置（弧形路径）
        start_x, start_y = self.start_pos
        target_x, target_y = self.target_pos

        # X轴线性插值
        self.current_pos[0] = start_x + (target_x - start_x) * eased_progress

        # Y轴弧形插值
        linear_y = start_y + (target_y - start_y) * eased_progress
        arc_offset = self.mid_height * math.sin(math.pi * progress)
        self.current_pos[1] = linear_y + arc_offset

        # 检查动画是否完成
        if progress >= 1.0:
            self.completed = True
            self.current_pos = list(self.target_pos)

    def draw(self, surface, scaled_images):
        """绘制飞行中的植物"""
        if self.completed:
            return

        # 植物类型到图片键名的映射
        image_map = {
            'sunflower': 'sunflower_60',
            'shooter': 'pea_shooter_60',
            'melon_pult': 'watermelon_60',
            'cattail': 'cattail_60',
            'wall_nut': 'wall_nut_60',
            'cherry_bomb': 'cherry_bomb_60',
            'cucumber': 'cucumber_60',
            'dandelion': 'dandelion_60',
            'lightning_flower': 'lightning_flower_60',
            'ice_cactus': 'ice_cactus_60'
        }

        img_key = image_map.get(self.plant_type)
        if img_key and img_key in scaled_images:
            img = scaled_images[img_key]

            # 计算缩放效果
            if self.reverse:
                scale_factor = 1.0 - 0.2 * (self.timer / self.duration)
            else:
                scale_factor = 0.8 + 0.2 * (1 - self.timer / self.duration)

            scaled_size = (int(img.get_width() * scale_factor),
                           int(img.get_height() * scale_factor))
            scaled_img = pygame.transform.scale(img, scaled_size)

            # 计算绘制位置
            draw_x = int(self.current_pos[0] - scaled_img.get_width() // 2)
            draw_y = int(self.current_pos[1] - scaled_img.get_height() // 2)

            surface.blit(scaled_img, (draw_x, draw_y))