"""
植物选择管理模块 - 负责管理植物选择界面和相关功能
支持第七卡槽
"""
import pygame
import sys
import os

# 添加父目录到路径以便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.constants import *
from core.cards_manager import get_plant_select_grid_new, cards_manager
from animation import PlantFlyingAnimation


class PlantSelectionManager:
    """植物选择管理器"""

    def __init__(self):
        # 植物选择状态
        self.show_plant_select = False  # 是否显示植物选择网格
        self.plant_select_grid = []  # 6×5植物网格

        # 植物飞行动画系统
        self.flying_plants = []  # 存储正在飞行的植物动画
        self.selected_plants_for_game = []  # 存储选中的植物类型

        # 初始化植物选择网格
        self.init_plant_select_grid()
        self.flying_selections = []  # 记录正在飞行的植物类型（用于立即UI反馈）

        # 添加game_manager引用用于检查第七卡槽
        self.game_manager = None

    def set_game_manager(self, game_manager):
        """设置game_manager引用，用于检查第七卡槽状态"""
        self.game_manager = game_manager

    def get_max_plant_slots(self):
        """获取最大植物槽位数量 - 修复：支持第七卡槽"""
        base_slots = 6
        if (self.game_manager and
                hasattr(self.game_manager, 'shop_manager') and
                self.game_manager.shop_manager.has_7th_card_slot()):
            return 7
        return base_slots

    def init_plant_select_grid(self, level_manager=None):
        """
        初始化6×5植物选择网格，根据关卡特性决定可用植物
        更新：使用特性管理系统
        """
        # 使用统一的接口获取植物选择网格 - 现在完全由特性管理系统控制
        self.plant_select_grid = get_plant_select_grid_new(level_manager)

        # 如果没有传入 level_manager，创建基础植物数据
        if not level_manager:
            # 基础植物（所有关卡都有）
            plants_data = [
                {'type': 'sunflower', 'name': '向日葵', 'cost': 50},
                {'type': 'shooter', 'name': '豌豆射手', 'cost': 75}
            ]

            # 填充6×5网格，多余槽位留空
            grid = []
            for row in range(5):
                grid_row = []
                for col in range(6):
                    index = row * 6 + col
                    if index < len(plants_data):
                        grid_row.append(plants_data[index])
                    else:
                        grid_row.append(None)  # 空槽位
                grid.append(grid_row)
            self.plant_select_grid = grid

    def get_selected_plant_cards(self):
        """获取已选择植物的卡片信息（用于植物选择界面显示）- 不包含飞行中的植物"""
        cards = []
        # 使用卡片管理器获取植物信息 - 统一管理
        for plant_type in self.selected_plants_for_game:
            card_info = cards_manager.get_card_info(plant_type)
            if card_info:
                cards.append(card_info.to_dict())

        return cards

    def start_plant_flying_animation(self, plant_data, source_rect):
        """开始植物正向飞行动画（选中）- 修复：支持第七卡槽"""
        # 修复：使用动态槽位数量检查
        max_slots = self.get_max_plant_slots()

        # 关键修复：计算选择后会达到的总数量
        # 已确认选择的 + 正在飞向卡槽的（正向飞行） + 准备选择的这一个
        current_confirmed = len(self.selected_plants_for_game)
        current_flying_to_slot = sum(1 for fp in self.flying_plants if not fp.reverse)
        total_after_selection = current_confirmed + current_flying_to_slot + 1

        # 如果选择这个植物后会超过最大槽位数，则阻止选择
        if total_after_selection > max_slots:
            return

        plant_type = plant_data['type']

        # 修复：检查该植物是否已经被选择（包括已确认选择、正在飞行、等待确认的）
        # 如果已经选择过这种植物，直接返回，不允许重复选择
        if plant_type in self.selected_plants_for_game:
            return

        # 检查是否有同类型植物正在飞行中
        for flying_plant in self.flying_plants:
            if flying_plant.plant_type == plant_type and not flying_plant.reverse:
                return  # 已有同类型植物在飞行中

        # 检查是否在临时选择列表中
        if plant_type in self.flying_selections:
            return

        # 立即添加到临时选择列表（用于UI立即反馈）
        self.flying_selections.append(plant_type)

        # 计算起始位置（源格子中心）
        start_pos = (source_rect.centerx, source_rect.centery)

        # 计算目标位置（卡片槽位置）
        target_slot_index = len(self.selected_plants_for_game) + len(
            [fp for fp in self.flying_plants if not fp.reverse])
        target_x = CARD_START_X + target_slot_index * CARD_WIDTH + CARD_WIDTH // 2
        target_y = CARD_Y + CARD_HEIGHT // 2
        target_pos = (target_x, target_y)

        # 创建正向飞行动画
        flying_plant = PlantFlyingAnimation(plant_data['type'], start_pos, target_pos, plant_data, reverse=False)
        self.flying_plants.append(flying_plant)

    def start_plant_unselect_animation(self, plant_type, card_slot_index):
        """开始植物反向飞行动画（取下）"""
        # 计算起始位置（卡片槽中心）
        start_x = CARD_START_X + card_slot_index * CARD_WIDTH + CARD_WIDTH // 2
        start_y = CARD_Y + CARD_HEIGHT // 2
        start_pos = (start_x, start_y)

        # 找到该植物类型在网格中的位置（找第一个匹配的）
        target_pos = None
        plant_data = None

        for row in range(len(self.plant_select_grid)):
            for col in range(len(self.plant_select_grid[row])):
                grid_plant = self.plant_select_grid[row][col]
                if grid_plant and grid_plant['type'] == plant_type:
                    # 计算网格位置
                    cell_width = GRID_SIZE
                    cell_height = GRID_SIZE
                    cell_spacing = 4

                    total_width = 6 * cell_width + (6 - 1) * cell_spacing
                    total_height = 5 * cell_height + (5 - 1) * cell_spacing
                    grid_start_x = BATTLEFIELD_LEFT + (total_battlefield_width - total_width) // 2
                    grid_start_y = BATTLEFIELD_TOP + (total_battlefield_height - total_height) // 2

                    target_x = grid_start_x + col * (cell_width + cell_spacing) + cell_width // 2
                    target_y = grid_start_y + row * (cell_height + cell_spacing) + cell_height // 2
                    target_pos = (target_x, target_y)
                    plant_data = grid_plant
                    break
            if target_pos:
                break

        if target_pos and plant_data:
            # 创建反向飞行动画
            flying_plant = PlantFlyingAnimation(plant_type, start_pos, target_pos, plant_data, reverse=True)
            self.flying_plants.append(flying_plant)

    def get_total_selected_count_for_ui(self):
        """获取用于UI显示的总选择计数（包括正在飞行的）- 修复：简化为每种植物0或1个"""
        selected_count_dict = {}

        # 统计已确认选择的植物（每种最多1个）
        for plant_type in self.selected_plants_for_game:
            selected_count_dict[plant_type] = 1  # 修复：每种植物只能有1个

        # 统计正在飞行的植物（每种最多1个）
        for plant_type in self.flying_selections:
            selected_count_dict[plant_type] = 1  # 修复：每种植物只能有1个

        return selected_count_dict

    def update_flying_plants(self):
        """更新植物飞行动画"""
        for flying_plant in self.flying_plants[:]:
            flying_plant.update()
            if flying_plant.completed:
                if flying_plant.reverse:
                    # 反向动画完成：从选中列表中移除植物
                    if flying_plant.plant_type in self.selected_plants_for_game:
                        self.selected_plants_for_game.remove(flying_plant.plant_type)
                else:
                    # 正向动画完成：将植物添加到选中列表
                    self.selected_plants_for_game.append(flying_plant.plant_type)
                    # 从临时列表中移除（新增）
                    if flying_plant.plant_type in self.flying_selections:
                        self.flying_selections.remove(flying_plant.plant_type)

                self.flying_plants.remove(flying_plant)

    def handle_card_slot_click(self, x, y):
        """处理卡片槽点击（用于取下植物）"""
        if not self.show_plant_select:
            return False

        # 检查点击是否在卡片区域
        for i, plant_type in enumerate(self.selected_plants_for_game):
            card_x = CARD_START_X + i * CARD_WIDTH
            card_rect = pygame.Rect(card_x, CARD_Y, CARD_WIDTH, CARD_HEIGHT)

            if card_rect.collidepoint(x, y):
                # 开始取下动画
                self.start_plant_unselect_animation(plant_type, i)

                # 立即从选中列表中移除（动画完成后会进一步确认）
                self.selected_plants_for_game.pop(i)
                return True

        return False

    def handle_plant_grid_click(self, x, y, plant_rects):
        """处理植物网格点击"""
        if not self.show_plant_select:
            return False

        # 处理植物格子点击
        for plant_rect, plant_data in plant_rects:
            if plant_rect.collidepoint(x, y):
                self.start_plant_flying_animation(plant_data, plant_rect)
                return True

        return False

    def show_plant_selection(self, level_manager=None):
        """显示植物选择界面"""
        self.show_plant_select = True
        # 重新初始化网格以反映当前关卡特性
        if level_manager:
            self.init_plant_select_grid(level_manager)

    def hide_plant_selection(self):
        """隐藏植物选择界面"""
        self.show_plant_select = False

    def clear_plant_selection_state(self):
        """清空植物选择相关的所有状态"""
        self.selected_plants_for_game = []
        self.flying_plants = []
        self.flying_selections = []
        self.show_plant_select = False

    def mark_returning_to_plant_select(self):
        """标记正在返回植物选择界面，用于保持植物选择状态"""
        self._returning_to_plant_select = True

    def should_show_plant_selection(self, level_num):
        """检查指定关卡是否应该显示植物选择"""
        return level_num >= 9  # 第9关及以上显示植物选择

    def get_selected_count(self):
        """获取已选择的植物数量"""
        return len(self.selected_plants_for_game)

    def is_selection_full(self):
        """检查是否已选满植物 - 修复：支持第七卡槽"""
        max_slots = self.get_max_plant_slots()
        return self.get_selected_count() >= max_slots

    def has_selected_plants(self):
        """检查是否有已选择的植物"""
        return len(self.selected_plants_for_game) > 0

    def get_plant_type_count(self, plant_type):
        """获取指定植物类型的选中数量 - 修复：每种植物最多1个"""
        return 1 if plant_type in self.selected_plants_for_game else 0

    def draw_flying_plants(self, surface, scaled_images):
        """绘制飞行中的植物"""
        for flying_plant in self.flying_plants:
            flying_plant.draw(surface, scaled_images)

    def is_plant_selection_active(self):
        """检查植物选择界面是否活跃"""
        return self.show_plant_select

    def reset_for_new_level(self, level_manager=None):
        """为新关卡重置植物选择状态"""
        # 清空选择状态
        self.clear_plant_selection_state()
        # 重新初始化网格
        self.init_plant_select_grid(level_manager)