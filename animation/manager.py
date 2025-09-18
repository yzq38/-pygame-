"""
动画管理器 - 统一管理所有动画效果的主控制器
"""
from .menu import MenuAnimationHandler
from .constants import *
from .effects import AnimationEffects


class AnimationManager:
    """动画管理器 - 管理游戏中的所有动画效果"""

    def __init__(self):
        # 初始化子管理器
        self.menu_handler = MenuAnimationHandler()
        self.effects = AnimationEffects()

        # 植物选择动画状态
        self.plant_select_animation_timer = 0
        self.plant_select_animation_complete = False
        self.plant_select_exit_animation = False
        self.plant_select_exit_timer = 0

        # 配置重载消息动画
        self.show_config_reload_message = False
        self.reload_message_timer = 0

    # 菜单动画委托给MenuAnimationHandler
    def start_menu_exit_animation(self, next_state):
        """开始主菜单退出动画"""
        self.menu_handler.start_menu_exit_animation(next_state)

    def start_level_select_exit_animation(self, next_state):
        """开始选关页面退出动画"""
        self.menu_handler.start_level_select_exit_animation(next_state)

    def update_menu_animations(self, current_game_state):
        """更新菜单相关的动画"""
        return self.menu_handler.update_menu_animations(current_game_state)

    def apply_menu_animation_transform(self, base_x, base_y, button_index=0):
        """应用菜单动画变换到按钮位置"""
        return self.menu_handler.apply_menu_animation_transform(base_x, base_y, button_index)

    def get_menu_animation_progress(self):
        """获取主菜单动画进度"""
        return self.menu_handler.get_menu_animation_progress()

    def get_level_select_animation_progress(self):
        """获取选关页面动画进度"""
        return self.menu_handler.get_level_select_animation_progress()

    def is_menu_exit_animating(self):
        """检查主菜单是否正在播放退出动画"""
        return self.menu_handler.is_menu_exit_animating()

    def is_level_select_exit_animating(self):
        """检查选关页面是否正在播放退出动画"""
        return self.menu_handler.is_level_select_exit_animating()

    def reset_menu_animation_states(self):
        """重置所有菜单动画状态"""
        self.menu_handler.reset_all_states()

    # 植物选择动画
    def start_plant_select_exit_animation(self):
        """开始植物选择界面退出动画"""
        self.plant_select_exit_animation = True
        self.plant_select_exit_timer = 0

    def update_plant_select_exit_animation(self):
        """更新植物选择退出动画"""
        if not self.plant_select_exit_animation:
            return False

        self.plant_select_exit_timer += 1

        if self.plant_select_exit_timer >= PLANT_SELECT_EXIT_DURATION:
            self.plant_select_exit_animation = False
            self.plant_select_exit_timer = 0
            return True

        return False

    def get_plant_select_exit_progress(self):
        """获取植物选择退出动画进度 (0-1)"""
        if not self.plant_select_exit_animation:
            return 0.0
        return min(1.0, self.plant_select_exit_timer / PLANT_SELECT_EXIT_DURATION)

    def is_plant_select_exit_animating(self):
        """检查植物选择是否正在播放退出动画"""
        return self.plant_select_exit_animation

    def reset_plant_select_animation(self):
        """重置植物选择动画状态"""
        self.plant_select_animation_timer = 0
        self.plant_select_animation_complete = False
        self.plant_select_exit_animation = False
        self.plant_select_exit_timer = 0

    def update_plant_select_animation(self):
        """更新植物选择动画"""
        if not self.plant_select_animation_complete:
            self.plant_select_animation_timer += 1
            if self.plant_select_animation_timer >= PLANT_SELECT_ANIMATION_DURATION:
                self.plant_select_animation_complete = True

    def get_plant_select_animation_progress(self):
        """获取植物选择动画进度"""
        return min(1.0, self.plant_select_animation_timer / PLANT_SELECT_ANIMATION_DURATION)

    # 配置重载消息
    def show_config_reload_notification(self):
        """显示配置重载通知"""
        self.show_config_reload_message = True
        self.reload_message_timer = 0

    def update_config_reload_message(self):
        """更新配置重载消息显示"""
        if self.show_config_reload_message:
            self.reload_message_timer += 1
            if self.reload_message_timer >= CONFIG_RELOAD_MESSAGE_DURATION:
                self.show_config_reload_message = False
                return False
        return self.show_config_reload_message

    def get_config_reload_message_alpha(self):
        """获取配置重载消息的透明度"""
        if not self.show_config_reload_message:
            return 0

        # 淡入淡出效果
        if self.reload_message_timer < 30:
            alpha = int(255 * (self.reload_message_timer / 30))
        elif self.reload_message_timer > CONFIG_RELOAD_MESSAGE_DURATION - 30:
            remaining = CONFIG_RELOAD_MESSAGE_DURATION - self.reload_message_timer
            alpha = int(255 * (remaining / 30))
        else:
            alpha = 255

        return alpha

    # 属性访问器（兼容旧代码）
    @property
    def menu_animation_timer(self):
        return self.menu_handler.menu_animation_timer

    @menu_animation_timer.setter
    def menu_animation_timer(self, value):
        self.menu_handler.menu_animation_timer = value

    @property
    def menu_animation_complete(self):
        return self.menu_handler.menu_animation_complete

    @property
    def menu_exit_animation(self):
        return self.menu_handler.menu_exit_animation

    @property
    def level_select_animation_timer(self):
        return self.menu_handler.level_select_animation_timer

    @level_select_animation_timer.setter
    def level_select_animation_timer(self, value):
        self.menu_handler.level_select_animation_timer = value

    @property
    def level_select_animation_complete(self):
        return self.menu_handler.level_select_animation_complete

    @property
    def level_select_exit_animation(self):
        return self.menu_handler.level_select_exit_animation

    @property
    def pending_next_state(self):
        return self.menu_handler.pending_next_state