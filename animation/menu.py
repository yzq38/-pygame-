"""
菜单动画处理器 - 负责菜单、选关、商店、图鉴等界面的动画
"""
from .constants import *
from .effects import AnimationEffects


class MenuAnimationHandler:
    """菜单动画处理器"""

    def __init__(self):
        self.effects = AnimationEffects()
        self.reset_all_states()

    def reset_all_states(self):
        """重置所有菜单动画状态"""
        # 主菜单
        self.menu_animation_timer = 0
        self.menu_animation_complete = False
        self.menu_exit_animation = False

        # 选关页面
        self.level_select_animation_timer = 0
        self.level_select_animation_complete = False
        self.level_select_exit_animation = False

        # 待切换状态
        self.pending_next_state = None

    def start_menu_exit_animation(self, next_state):
        """开始主菜单退出动画"""
        self.menu_exit_animation = True
        self.menu_animation_timer = 0
        self.pending_next_state = next_state

    def start_level_select_exit_animation(self, next_state):
        """开始选关页面退出动画"""
        self.level_select_exit_animation = True
        self.menu_animation_timer = 0
        self.pending_next_state = next_state

    def update_menu_animations(self, current_game_state):
        """更新菜单相关的动画"""
        if current_game_state == "main_menu":
            return self._update_main_menu_animation()
        elif current_game_state in ["level_select", "shop", "codex"]:
            return self._update_level_select_animation(current_game_state)
        else:
            self.reset_all_states()
            return None

    def _update_main_menu_animation(self):
        """更新主菜单动画"""
        if self.menu_exit_animation:
            self.menu_animation_timer += 1
            if self.menu_animation_timer >= MENU_EXIT_DURATION:
                next_state = self.pending_next_state
                self.menu_exit_animation = False
                self.pending_next_state = None

                if next_state in ["level_select", "shop", "codex"]:
                    self.level_select_animation_timer = 0
                    self.level_select_animation_complete = False
                return next_state
        else:
            if not self.menu_animation_complete:
                self.menu_animation_timer += 1
                if self.menu_animation_timer >= MENU_ANIMATION_DURATION:
                    self.menu_animation_complete = True
        return None

    def _update_level_select_animation(self, current_state):
        """更新选关/商店/图鉴页面动画"""
        if self.level_select_exit_animation:
            self.menu_animation_timer += 1
            if self.menu_animation_timer >= LEVEL_SELECT_EXIT_DURATION:
                next_state = self.pending_next_state
                self.level_select_exit_animation = False
                self.pending_next_state = None
                self.menu_animation_timer = 0
                self.menu_animation_complete = False
                return next_state
        else:
            if not self.level_select_animation_complete:
                self.level_select_animation_timer += 1
                if self.level_select_animation_timer >= LEVEL_SELECT_ANIMATION_DURATION:
                    self.level_select_animation_complete = True
        return None

    def apply_menu_animation_transform(self, base_x, base_y, button_index=0):
        """应用菜单动画变换到按钮位置"""
        if self.menu_exit_animation:
            return self._apply_exit_transform(base_x, base_y, button_index)
        else:
            return self._apply_entrance_transform(base_x, base_y, button_index)

    def _apply_exit_transform(self, base_x, base_y, button_index):
        """应用退出动画变换"""
        button_exit_start = button_index * BUTTON_EXIT_STAGGER_DELAY
        button_exit_time = max(0, self.menu_animation_timer - button_exit_start)

        if button_exit_time > 0:
            exit_duration = MENU_EXIT_DURATION - button_exit_start
            exit_progress = min(1.0, button_exit_time / exit_duration)
            eased_exit_progress = self.effects.ease_in_cubic(exit_progress)

            from constants import BASE_WIDTH
            start_x = base_x
            end_x = BASE_WIDTH + 100
            current_x = start_x + (end_x - start_x) * eased_exit_progress

            alpha = int(255 * (1 - exit_progress))
            return current_x, base_y, alpha
        else:
            return base_x, base_y, 255

    def _apply_entrance_transform(self, base_x, base_y, button_index):
        """应用入场动画变换"""
        button_start_time = button_index * BUTTON_STAGGER_DELAY
        button_current_time = max(0, self.menu_animation_timer - button_start_time)
        progress = min(1.0, button_current_time / BUTTON_ANIMATION_DURATION)
        eased_progress = self.effects.ease_out_cubic(progress) if progress > 0 else 0

        from core.constants import BASE_WIDTH
        start_x = BASE_WIDTH + 50
        end_x = base_x
        current_x = start_x + (end_x - start_x) * eased_progress
        alpha = int(255 * eased_progress)

        return current_x, base_y, alpha

    def get_menu_animation_progress(self):
        """获取主菜单动画进度"""
        if self.menu_exit_animation:
            return min(1.0, self.menu_animation_timer / MENU_EXIT_DURATION)
        else:
            return min(1.0, self.menu_animation_timer / MENU_ANIMATION_DURATION)

    def get_level_select_animation_progress(self):
        """获取选关页面动画进度"""
        if self.level_select_exit_animation:
            return min(1.0, self.menu_animation_timer / LEVEL_SELECT_EXIT_DURATION)
        else:
            return min(1.0, self.level_select_animation_timer / LEVEL_SELECT_ANIMATION_DURATION)

    def is_menu_exit_animating(self):
        """检查主菜单是否正在播放退出动画"""
        return self.menu_exit_animation

    def is_level_select_exit_animating(self):
        """检查选关页面是否正在播放退出动画"""
        return self.level_select_exit_animation