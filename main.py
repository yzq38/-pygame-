"""
主程序文件 - 植物大战僵尸贴图版
重构版本 - 更新导入路径到rsc_mng文件夹
"""
import math
import pygame
import random
import sys
import os
from animation import AnimationManager, PlantFlyingAnimation, Trophy
from core.constants import *
from rsc_mng.audio_manager import BackgroundMusicManager, initialize_sounds, play_sound_with_music_pause, set_sounds_volume
from performance import PerformanceMonitor
from rsc_mng.resource_loader import load_all_images, preload_scaled_images, initialize_fonts, get_images
from database import GameDatabase, auto_save_game_progress, restore_game_from_save, check_level_has_save
from core.game_logic import (
    create_zombie_for_level, update_bullets, update_plant_shooting,
    update_dandelion_seeds, update_hammer_cooldown, handle_plant_placement,
    spawn_zombie_wave_fixed, update_card_cooldowns,
    handle_cucumber_fullscreen_explosion, update_cucumber_effects,
    update_freeze_effects, is_zombie_stunned, is_zombie_spraying,
    add_sun_safely,initialize_portal_system, update_portal_system, update_zombie_portal_interaction
)
from core.level_manager import LevelManager
from core.cards_manager import get_plant_select_grid_new, cards_manager, get_available_cards_new
from shop import ShopManager, CartManager
from core.game_state_manager import GameStateManager
from core.event_handler import EventHandler
from ui import PlantSelectionManager,RendererManager,PortalManager




class GameManager:
    """简化后的游戏管理器 - 协调各种专职管理器 levels"""

    def __init__(self):
        # 初始化Pygame

        pygame.init()
        pygame.mixer.init()

        # 创建游戏窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("植物大战僵尸简易版")
        self.clock = pygame.time.Clock()

        # 全屏状态变量
        self.fullscreen = False
        self.screen_offset_x = 0
        self.screen_offset_y = 0
        self.screen_scale = 1.0

        # 热重载相关设置
        self.hot_reload_enabled = True  # 默认启用热重载

        # 初始化资源
        self.fonts = initialize_fonts()
        self.font_small, self.font_medium, self.font_large, self.font_tiny = self.fonts
        self.images = load_all_images()
        self.scaled_images = preload_scaled_images()
        self.sounds = initialize_sounds()

        # 初始化各种管理器
        self.music_manager = BackgroundMusicManager()
        self.performance_monitor = PerformanceMonitor()
        self.game_db = GameDatabase()
        # 为状态管理器设置数据库引用
        self.state_manager = GameStateManager()
        self.state_manager.game_db = self.game_db  # 传递数据库引用
        self.plant_selection_manager = PlantSelectionManager()
        self.plant_selection_manager.game_manager = self


        # 专职管理器

        self.animation_manager = AnimationManager()

        self.event_handler = EventHandler(self)
        self.renderer_manager = RendererManager(self)

        # 游戏状态和设置
        self.level_settings = self.game_db.get_level_settings()
        self.game = self.state_manager.reset_game()

        # 音量设置
        self.volume = 0.7
        pygame.mixer.music.set_volume(self.volume)
        set_sounds_volume(self.sounds, self.volume)

        # 铲子配置
        self.shovel = {
            "x": SHOVEL_X, "y": SHOVEL_Y,
            "width": SHOVEL_WIDTH, "height": SHOVEL_HEIGHT,
            "color": SHOVEL_COLOR
        }

        # 游戏表面
        self.game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        self.shop_manager = ShopManager()
        self.coins = self.game_db.get_coins()

        # 初始化小推车管理器
        self.cart_manager = CartManager(self.shop_manager, self.images, self.sounds)
        # 确保锤子相关的初始化
        # 游戏状态中初始化锤子冷却时间
        if self.game and "hammer_cooldown" not in self.game:
            self.game["hammer_cooldown"] = 0
        # 确保传送门管理器的初始化字段存在
        if self.game and "portal_manager" not in self.game:
            self.game["portal_manager"] = None

        # 确保商店管理器有锤子检查方法
        if not hasattr(self.shop_manager, 'has_hammer'):
            # 为商店管理器添加锤子检查方法
            def has_hammer():
                return self.shop_manager.is_purchased('hammer')

            self.shop_manager.has_hammer = has_hammer



    def reset_carts(self):
        """重置小推车系统"""
        self.cart_manager.reset_all_carts()

    def reset_portal_system(self):
        """重置传送门系统"""
        if "portal_manager" in self.game:
            self.game["portal_manager"] = None

    def _handle_coin_drop(self):
        """处理僵尸死亡时的金币掉落"""
        coin_drop_chance = random.random()
        if coin_drop_chance < 0.01:  # 1%概率掉落10￥
            self.add_coins(10)
        elif coin_drop_chance < 0.06:  # 5%概率掉落5￥（累计概率6%，所以是5%）
            self.add_coins(5)
        elif coin_drop_chance < 0.16:  # 10%概率掉落1￥（累计概率16%，所以是10%）
            self.add_coins(1)

    def add_coins(self, amount):
        """安全地增加金币数量"""
        self.coins += amount
        if self.coins < 0:
            self.coins = 0
        # 同步保存到数据库
        self.game_db.set_coins(self.coins)

    def toggle_fullscreen(self):
        """切换全屏模式"""
        if not self.fullscreen:
            # 切换到全屏
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.fullscreen = True
        else:
            # 切换到窗口模式
            self.screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT))
            self.fullscreen = False

        # 更新屏幕尺寸
        screen_width, screen_height = self.screen.get_size()

        # 计算缩放比例和偏移量，以保持游戏内容居中
        if self.fullscreen:
            # 计算保持宽高比的缩放
            scale_x = screen_width / BASE_WIDTH
            scale_y = screen_height / BASE_HEIGHT
            self.screen_scale = min(scale_x, scale_y)

            # 计算偏移量以使内容居中
            self.screen_offset_x = (screen_width - BASE_WIDTH * self.screen_scale) / 2
            self.screen_offset_y = (screen_height - BASE_HEIGHT * self.screen_scale) / 2
        else:
            self.screen_scale = 1.0
            self.screen_offset_x = 0
            self.screen_offset_y = 0

    def transform_mouse_pos(self, pos):
        """转换鼠标位置到游戏坐标"""
        x, y = pos
        if self.fullscreen:
            # 转换全屏坐标到游戏坐标
            x = (x - self.screen_offset_x) / self.screen_scale
            y = (y - self.screen_offset_y) / self.screen_scale
        return x, y

    def update_game_logic(self):
        """更新游戏逻辑"""
        # 更新过渡动画
        should_load_game = self.state_manager.update_transition_animation()
        if should_load_game:
            self.load_pending_game_data()

        # 更新菜单动画
        new_state = self.animation_manager.update_menu_animations(self.state_manager.game_state)
        if new_state:
            self.state_manager.game_state = new_state

        # 更新植物选择动画和飞行动画（即使游戏逻辑暂停也要更新）
        if self.plant_selection_manager.show_plant_select:
            self.animation_manager.update_plant_select_animation()
            self.plant_selection_manager.update_flying_plants()

            # 更新植物选择退出动画
            exit_animation_complete = self.animation_manager.update_plant_select_exit_animation()
            if exit_animation_complete:
                # 退出动画完成，真正隐藏植物选择界面并开始游戏
                self.plant_selection_manager.hide_plant_selection()
                self.state_manager.game_paused = False

        # 更新配置重载消息显示额外
        self.animation_manager.update_config_reload_message()

        # 在过渡动画期间或菜单退出动画期间暂停游戏逻辑更新
        if (self.state_manager.is_in_transition() or
                self.animation_manager.is_menu_exit_animating()):
            return
        # 同步待处理的金币
        if '_pending_coins' in self.game and self.game['_pending_coins'] > 0:
            self.add_coins(self.game['_pending_coins'])
            self.game['_pending_coins'] = 0
        # 更新游戏主逻辑
        if (self.state_manager.game_state == "playing" and
                not self.game["game_over"] and
                not self.state_manager.should_pause_game_logic() and
                not self.plant_selection_manager.show_plant_select):  # 植物选择界面显示时暂停游戏逻辑

            # 检查配置文件是否更新
            if self.hot_reload_enabled and self.game["level_manager"].check_hot_reload():
                self.animation_manager.show_config_reload_notification()

            # 更新卡片冷却时间
            update_card_cooldowns(self.game)

            # 自动保存游戏进度（每5秒保存一次）
            if not self.game.get("level_completed", False):
                auto_save_game_progress(self.game_db, self.game, self.music_manager, self, save_interval=100)

            # 设置图片引用
            self._set_object_references()

            # 执行主游戏逻辑更新
            self._update_main_game_logic()

    def _set_object_references(self):
        """设置游戏对象的图片和音效引用"""
        for plant in self.game["plants"]:
            plant.images = self.images
        for zombie in self.game["zombies"]:
            zombie.images = self.images
            zombie.sounds = self.sounds
        for bullet in self.game["bullets"]:
            bullet.images = self.images
        if "dandelion_seeds" in self.game:
            for seed in self.game["dandelion_seeds"]:
                seed.images = self.images

        # 设置小推车的图片和声音引用
        self.cart_manager.images = self.images
        self.cart_manager.sounds = self.sounds
        for cart in self.cart_manager.carts.values():
            cart.images = self.images
            cart.sounds = self.sounds

    def _apply_damage_to_zombie(self, zombie, damage):
        """正确处理对僵尸的伤害：先消耗防具血量，再消耗本体血量"""
        remaining_damage = damage

        # 如果僵尸有防具且防具血量大于0，先消耗防具血量
        if zombie.has_armor and zombie.armor_health > 0:
            if remaining_damage >= zombie.armor_health:
                # 伤害足够摧毁防具
                remaining_damage -= zombie.armor_health
                zombie.armor_health = 0
            else:
                # 伤害不足以摧毁防具
                zombie.armor_health -= remaining_damage
                remaining_damage = 0

        # 如果还有剩余伤害，对本体造成伤害
        if remaining_damage > 0:
            zombie.health -= remaining_damage
            # 确保血量不会变成负数
            zombie.health = max(0, zombie.health)

    def _update_main_game_logic(self):
        """更新主要游戏逻辑"""
        # 1. 更新植物（向日葵产阳光）- 只调用一次
        update_plant_shooting(self.game, self.game["level_manager"], sounds=self.sounds)

        # 检查樱桃炸弹音效触发（直接检查植物状态）
        for plant in self.game["plants"]:
            if plant.plant_type == "cherry_bomb":
                # 检查是否需要播放爆炸音效
                if plant.should_play_explosion_sound():
                    if self.sounds.get("cherry_explosion"):
                        self.sounds["cherry_explosion"].play()
                    plant.mark_sound_played()
            elif plant.plant_type == "cucumber":
                # 检查黄瓜是否需要播放爆炸音效
                if plant.should_play_explosion_sound():
                    if self.sounds.get("cherry_explosion"):
                        self.sounds["cherry_explosion"].play()
                    plant.mark_sound_played()

        # 2. 更新僵尸（移动/攻击）- 这里僵尸可能会攻击植物
        self._update_zombies()

        # 3. 检查所有植物的状态，特别处理樱桃炸弹和黄瓜
        self._handle_plant_deaths_and_explosions()

        # 4. 计算进入波次模式需要的击杀数量
        level_mgr = self.game["level_manager"]
        required_kills = level_mgr.max_waves * 5

        # 5. 检查是否进入波次模式
        if not self.game["wave_mode"] and self.game["zombies_killed"] >= required_kills:
            self.game["wave_mode"] = True
            self.game["level_manager"].start_wave_mode()
            self.game["wave_timer"] = 0

        # 6. 僵尸生成逻辑
        if self.game["wave_mode"]:
            self._update_wave_mode_spawning()
        else:
            self._update_normal_mode_spawning()

        # 7. 检查是否所有波次完成
        self._check_level_completion()

        # 8. 更新奖杯
        self._update_trophy()

        # 9. 处理淡入淡出效果
        self._update_fade_effects()

        # 10. 更新子弹（移动/碰撞）- 移除重复调用
        update_bullets(self.game, self.game["level_manager"], self.level_settings, self.sounds)
        # 更新蒲公英种子
        update_dandelion_seeds(self.game, self.game["level_manager"], self.level_settings, self.sounds)

        # 11. 随机增加阳光（每帧0.9%概率+5）- 添加阳光上限检查
        if random.random() < 0.01:
            self.game["sun"] = add_sun_safely(self.game["sun"], 5)

        # 12. 更新黄瓜效果状态
        update_cucumber_effects(self.game, self.sounds)

        # 13. 更新锤子冷却时间
        self._update_hammer_cooldown()

        # 14. 更新小推车系统
        self._update_cart_system()
        # 15. 更新传送门系统
        self._update_portal_system()

    def _update_hammer_cooldown(self):
        """更新锤子冷却时间"""
        if "hammer_cooldown" in self.game and self.game["hammer_cooldown"] > 0:
            self.game["hammer_cooldown"] -= 1
            if self.game["hammer_cooldown"] <= 0:
                self.game["hammer_cooldown"] = 0

    def _update_portal_system(self):
        """更新传送门系统，增加安全检查和自动修复"""
        # 检查是否应该有传送门但缺少传送门管理器
        level_manager = self.game.get("level_manager")
        if level_manager:
            should_have_portals = level_manager.has_special_feature("portal_system")
            current_portal_manager = self.game.get("portal_manager")

            # 如果应该有传送门但没有管理器，重新初始化
            if should_have_portals and not current_portal_manager:
                print(f"检测到传送门缺失，重新初始化传送门系统")
                initialize_portal_system(self.game, level_manager)
                return

        # 更新传送门管理器状态
        if "portal_manager" in self.game and self.game["portal_manager"]:
            update_portal_system(self.game)
            # 处理僵尸与传送门的交互
            update_zombie_portal_interaction(self.game)

    def _update_cart_system(self):
        """更新小推车系统"""
        # 检查僵尸是否触发小推车
        self.cart_manager.check_zombie_trigger(self.game["zombies"])

        # 更新小推车状态并处理碰撞
        hit_zombies = self.cart_manager.update_carts(self.game["zombies"])

        # 处理被小推车撞击的僵尸
        for zombie in hit_zombies:
            if zombie in self.game["zombies"]:
                # 立即开始死亡动画
                zombie.start_death_animation()

    def _handle_plant_deaths_and_explosions(self):
        """
        处理植物死亡和樱桃炸弹、黄瓜爆炸逻辑
        新增方法：确保樱桃炸弹和黄瓜在被啃咬死亡时也能正确爆炸
        """
        plants_to_remove = []

        for plant in self.game["plants"]:
            if plant.plant_type in ["cherry_bomb", "cucumber"]:
                # 特殊处理爆炸植物
                if plant.health <= 0 and not plant.has_exploded:
                    # 被啃咬死亡，立即触发爆炸
                    if plant.plant_type == "cherry_bomb":
                        plant.explode()
                    elif plant.plant_type == "cucumber":
                        plant.explode_cucumber()

                # 检查是否刚刚爆炸（立即处理伤害）
                if plant.has_exploded and not hasattr(plant, '_damage_applied'):
                    if plant.plant_type == "cherry_bomb":
                        # 樱桃炸弹：处理3x3范围伤害
                        explosion_area = plant.get_explosion_area()
                        for zombie in self.game["zombies"]:
                            zombie_grid_row = zombie.row
                            zombie_grid_col = int(round(zombie.col))
                            if (zombie_grid_row, zombie_grid_col) in explosion_area:
                                self._apply_damage_to_zombie(zombie, plant.explosion_damage)

                    elif plant.plant_type == "cucumber":
                        # 黄瓜：处理全屏效果
                        cucumber_explosion_data = plant.get_fullscreen_explosion_data()
                        if cucumber_explosion_data:
                            handle_cucumber_fullscreen_explosion(self.game, cucumber_explosion_data, self.sounds)

                    # 标记伤害已应用，避免重复伤害
                    plant._damage_applied = True

                # 检查爆炸植物是否应该被移除（爆炸动画完成）
                if plant.should_be_removed:
                    plants_to_remove.append(plant)

            else:
                # 处理其他植物的死亡
                if plant.health <= 0:
                    plants_to_remove.append(plant)

        # 移除已死亡的植物（爆炸植物等爆炸完成后移除）
        for plant in plants_to_remove:
            if plant in self.game["plants"]:
                self.game["plants"].remove(plant)
                # 如果是向日葵死亡，更新计数
                if plant.plant_type == "sunflower":
                    self.game["level_manager"].remove_sunflower()

    def _update_wave_mode_spawning(self):
        """更新波次模式下的僵尸生成 - 修复版本"""
        level_mgr = self.game["level_manager"]
        if not level_mgr.wave_mode:
            level_mgr.start_wave_mode()

        self.game["wave_timer"] += 1
        if self.game["wave_timer"] >= WAVE_INTERVAL and level_mgr.current_wave < level_mgr.max_waves:
            zombies_per_row = [random.randint(3, 4) for _ in range(GRID_HEIGHT)]
            total_zombie_count = sum(zombies_per_row)

            #  修复：先正式开始波次
            level_mgr.start_wave(total_zombie_count)

            #  修复：再生成僵尸
            spawn_zombie_wave_fixed(self.game, level_mgr.current_wave == 1, zombies_per_row, self.sounds)

            self.game["wave_timer"] = 0

    def _update_normal_mode_spawning(self):
        """更新普通模式下的僵尸生成"""
        self.game["zombie_timer"] += 1
        if (self.game["zombie_timer"] >= NORMAL_SPAWN_DELAY and
                len(self.game["zombies"]) < 10 and
                self.game["zombies_spawned"] < MAX_NORMAL_ZOMBIES):
            zombie = create_zombie_for_level(
                random.randint(0, GRID_HEIGHT - 1),
                self.game["level_manager"],
                False,
                self.level_settings
            )
            zombie.images = self.images
            zombie.sounds = self.sounds
            self.game["zombies"].append(zombie)
            self.game["zombies_spawned"] += 1
            self.game["zombie_timer"] = 0

    def _update_zombies(self):
        """更新僵尸状态（添加阳光上限检查）"""

        for zombie in self.game["zombies"][:]:
            # 如果僵尸处于死亡动画状态，只更新死亡动画
            if zombie.is_dying:
                zombie.update(self.game["plants"])
                # 检查死亡动画是否结束
                if zombie.death_animation_timer <= 0:
                    self.game["zombies"].remove(zombie)

                    # 更新击杀计数器（只在非波次模式下计算）
                    if not self.game["wave_mode"]:
                        self.game["zombies_killed"] += 1

                    should_drop_sun = True

                    if self.game["wave_mode"]:
                        # 使用特性管理系统检查是否掉落阳光
                        level_mgr = self.game["level_manager"]
                        if level_mgr.no_sun_drop_in_wave_mode():
                            should_drop_sun = False

                    if should_drop_sun:
                        # 修改：使用特性管理系统检查随机阳光掉落，并添加阳光上限检查
                        level_mgr = self.game["level_manager"]
                        if level_mgr.has_special_feature("random_sun_drop"):
                            # 随机掉落5或10阳光
                            sun_amount = random.choice([5, 10])
                            self.game["sun"] = add_sun_safely(self.game["sun"], sun_amount)
                        else:
                            # 默认掉落20阳光
                            self.game["sun"] = add_sun_safely(self.game["sun"], 20)
                    self._handle_coin_drop()
                    if self.game["wave_mode"]:
                        self.game["level_manager"].zombie_defeated()
                continue
            # 检查僵尸是否被眩晕，眩晕状态下不更新
            if not is_zombie_stunned(self.game, zombie):
                zombie.update(self.game["plants"])

            # 检查僵尸是否正在喷射，如果是则创建喷射粒子
            # 修改：降低粒子创建频率，每10帧创建一次，而不是每帧都创建
            if is_zombie_spraying(self.game, zombie):
                # 添加一个计数器，每10帧创建一次粒子
                if not hasattr(zombie, 'spray_particle_timer'):
                    zombie.spray_particle_timer = 0

                zombie.spray_particle_timer += 1

                # 每10帧创建一次粒子，而且数量固定为1-2个
                if zombie.spray_particle_timer >= 10:
                    zombie.spray_particle_timer = 0

                    # 为僵尸的当前位置创建喷射粒子
                    zombie_x = (BATTLEFIELD_LEFT +
                                zombie.col * (GRID_SIZE + GRID_GAP) +
                                GRID_SIZE // 2)
                    zombie_y = (BATTLEFIELD_TOP +
                                zombie.row * (GRID_SIZE + GRID_GAP) +
                                GRID_SIZE // 2)

                    # 查找黄瓜植物来创建喷射粒子
                    for plant in self.game["plants"]:
                        if plant.plant_type == "cucumber" and hasattr(plant, 'create_spray_particles_at_position'):
                            # 僵尸面向左侧（direction=-1）
                            plant.create_spray_particles_at_position(zombie_x, zombie_y, direction=-1)
                            break

            # 修改：使用僵尸中心点检查边界碰撞，而不是僵尸图片边缘
            zombie_center_col = zombie.col + 0.3  # 僵尸中心点位置（假设僵尸宽度为0.6格）

            # 当僵尸中心点到达战场左边界时触发游戏结束
            if zombie_center_col < 0:
                # 检查该行是否有可用的小推车
                if self.cart_manager.has_cart_in_row(zombie.row):
                    # 触发小推车，但不立即游戏结束
                    self.cart_manager.trigger_cart_in_row(zombie.row)
                else:
                    # 没有小推车，游戏结束
                    self.game["game_over"] = True
                    if not self.game["game_over_sound_played"] and self.sounds.get("game_over"):
                        play_sound_with_music_pause(self.sounds["game_over"], music_manager=self.music_manager)
                        self.game["game_over_sound_played"] = True

            if zombie.health <= 0 and not zombie.is_dying:
                # 开始死亡动画，而不是立即移除
                zombie.start_death_animation()

                # 更新击杀计数器（只在非波次模式下计算）
                if not self.game["wave_mode"]:
                    self.game["zombies_killed"] += 1

                should_drop_sun = True
                if self.game["wave_mode"]:
                    # 使用特性管理系统检查是否掉落阳光
                    level_mgr = self.game["level_manager"]
                    if level_mgr.no_sun_drop_in_wave_mode():
                        should_drop_sun = False

                if should_drop_sun:
                    # 修改：使用特性管理系统检查随机阳光掉落，并添加阳光上限检查
                    level_mgr = self.game["level_manager"]
                    if level_mgr.has_special_feature("random_sun_drop"):
                        # 随机掉落5或10阳光
                        sun_amount = random.choice([5, 10])
                        self.game["sun"] = add_sun_safely(self.game["sun"], sun_amount)
                    else:
                        # 默认掉落20阳光
                        self.game["sun"] = add_sun_safely(self.game["sun"], 20)
                self._handle_coin_drop()

                if self.game["wave_mode"]:
                    self.game["level_manager"].zombie_defeated()
                coin_drop_chance = random.random()
                if coin_drop_chance < 0.01:  # 1%概率掉落10￥
                    self.add_coins(10)
                elif coin_drop_chance < 0.06:  # 5%概率掉落5￥（累计概率6%，所以是5%）
                    self.add_coins(5)
                elif coin_drop_chance < 0.16:  # 10%概率掉落1￥（累计概率16%，所以是10%）
                    self.add_coins(1)

    def _check_level_completion(self):
        """检查关卡是否完成"""
        level_mgr = self.game["level_manager"]
        if (self.game["wave_mode"] and level_mgr.all_waves_completed and
                not level_mgr.trophy and len(self.game["zombies"]) == 0 and
                level_mgr.current_wave >= level_mgr.max_waves):
            trophy_x = BASE_WIDTH // 2 - 30
            trophy_y = BASE_HEIGHT // 2 - 40
            level_mgr.create_trophy(trophy_x, trophy_y, self.images.get('trophy_img'))
            # 奖杯出现时立即清除保存进度和标记通关
            current_game_level = level_mgr.current_level
            self.game_db.mark_level_completed(current_game_level)
            self.game_db.clear_saved_game(current_game_level)
            self.game["level_completed"] = True

    def _update_trophy(self):
        """更新奖杯状态"""
        level_mgr = self.game["level_manager"]
        if level_mgr.trophy:
            level_mgr.trophy.update()
            if level_mgr.trophy.explosion_complete and self.game["fade_state"] == "none":
                self.game["fade_state"] = "fading_out"
                self.game["fade_timer"] = 0

    def _update_fade_effects(self):
        """更新淡入淡出效果"""
        if self.game["fade_state"] != "none":
            self.game["fade_timer"] += 1
            if self.game["fade_state"] == "fading_out":
                self.game["fade_alpha"] = min(255,
                                              int(255 * (self.game["fade_timer"] / self.game["fade_duration"])))
                if self.game["fade_timer"] >= self.game["fade_duration"]:
                    self.game["fade_state"] = "fading_in"
                    self.game["fade_timer"] = 0
                    self.state_manager.switch_to_level_select()
                    self.game = self.state_manager.reset_game()
            elif self.game["fade_state"] == "fading_in":
                self.game["fade_alpha"] = max(0, 255 - int(
                    255 * (self.game["fade_timer"] / self.game["fade_duration"])))
                if self.game["fade_timer"] >= self.game["fade_duration"]:
                    self.game["fade_state"] = "none"
                    self.game["fade_alpha"] = 0

    def get_available_cards_for_current_state(self):
        """获取当前状态下的可用卡片 - 修复：支持第七卡槽，解决空选择状态bug"""
        if self.plant_selection_manager.show_plant_select:
            # 植物选择期间：只显示已完成选择的植物卡片（不包含飞行中的）
            return self.plant_selection_manager.get_selected_plant_cards()
        elif (self.game["level_manager"].current_level >= 9 and
              self.plant_selection_manager.has_selected_plants()):
            # 已选择植物，显示选中的植物卡片
            base_cards = get_available_cards_new(self.game["level_manager"], self.level_settings,
                                                 self.plant_selection_manager.selected_plants_for_game)
        else:
            # 修复：第8关及以下，或者第9关以上但没有选择植物时，使用默认植物
            # 关键修复：确保即使在第9关以上，如果没有选择植物也要显示所有可用植物
            if self.game["level_manager"].current_level >= 9:
                # 第9关以上但没有选择植物时，显示所有可用植物供选择
                # 而不是应用任何限制
                base_cards = get_available_cards_new(self.game["level_manager"], self.level_settings,
                                                     None)
            else:
                # 第8关及以下，使用默认植物
                base_cards = get_available_cards_new(self.game["level_manager"], self.level_settings, None)

        # 修复：检查是否购买了第七卡槽，如果购买了但卡片不足7张，则补充
        if hasattr(self, 'shop_manager') and self.shop_manager.has_7th_card_slot():
            if len(base_cards) < 7:
                # 定义可添加的额外植物卡片池
                extra_plant_cards = [
                    # 这里可以添加额外的植物卡片，如果需要的话
                ]

                # 计算需要添加的卡片数量
                cards_needed = 7 - len(base_cards)

                # 从额外卡片池中添加卡片，但不超过可用的额外植物数量
                for i in range(min(cards_needed, len(extra_plant_cards))):
                    # 确保不添加重复的植物类型
                    extra_card = extra_plant_cards[i]
                    if not any(card["type"] == extra_card["type"] for card in base_cards):
                        base_cards.append(extra_card.copy())

                    # 如果已经凑够7张卡，停止添加
                    if len(base_cards) >= 7:
                        break

        return base_cards

    def should_save_game_on_exit(self):
        """
        检查游戏退出时是否应该保存游戏进度
        修复：改进植物选择页面状态判断
        """
        # 如果游戏不在进行中或已经结束，不保存
        if self.state_manager.game_state != "playing" or self.game["game_over"]:
            return False

        # 获取当前关卡
        current_level = self.game["level_manager"].current_level

        # 第9关及以后的关卡需要特殊处理
        if current_level >= 9:
            # 修复：如果正在显示植物选择界面但还未选择任何植物，不保存
            # 这样可以避免保存空的植物选择状态
            if (self.plant_selection_manager.show_plant_select and
                    not self.plant_selection_manager.has_selected_plants()):
                return False
            # 其他情况都保存（包括植物选择页面有已选植物的情况）
            return True

        # 第8关及以下的关卡，只有不在植物选择界面时才保存
        return not self.plant_selection_manager.show_plant_select

    def load_pending_game_data(self):
        """
        加载待处理的游戏数据
        修复：改进植物选择状态的恢复逻辑
        """
        pending_data, pending_level = self.state_manager.get_pending_game_data()

        if pending_data:
            # 加载保存的游戏
            level_manager = LevelManager("database/levels.json")
            level_manager.start_level(pending_level)
            # 修改：传入 game_manager 参数以恢复植物选择状态
            restored_game = restore_game_from_save(pending_data, level_manager, self)
            if restored_game:
                self.game = restored_game
                music_state = pending_data.get("music_state", {})
                self.music_manager.restore_music_state(music_state)

                # 恢复小推车状态
                cart_data = pending_data.get("cart_data", {})
                if cart_data:
                    self.cart_manager.load_save_data(cart_data)
                else:
                    # 如果没有小推车数据，重新初始化
                    self.cart_manager.reinitialize_carts()
            else:
                self.game_db.clear_saved_game(pending_level)
                self.game = self.state_manager.reset_game(pending_level)
                # 新游戏时重置小推车
                self.reset_carts()
        else:
            # 开始新游戏
            self.game = self.state_manager.reset_game(pending_level)
            # 新游戏时重置小推车
            self.reset_carts()

        # 立即设置图片和声音引用，避免过渡动画期间显示颜色块
        self._set_object_references()
        # 只有在没有传送门管理器或者是新游戏时才初始化传送门系统
        level_manager = self.game.get("level_manager")
        if level_manager:
            # 检查是否已经有传送门管理器（从保存数据恢复的）
            existing_portal_manager = self.game.get("portal_manager")

            if existing_portal_manager is None:
                # 没有传送门管理器，需要初始化（新游戏或不支持传送门的关卡）
                initialize_portal_system(self.game, level_manager)

            else:
                # 已有传送门管理器（从保存数据恢复），不重新初始化
                pass

                # 只需要设置传送门的图片引用，不重新初始化位置
                if hasattr(existing_portal_manager, 'portals'):
                    for portal in existing_portal_manager.portals:
                        # 传送门不需要images属性，这里预留给将来可能的扩展
                        pass

        # 切换到游戏状态
        self.state_manager.switch_to_game_state()

        # 修复：植物选择界面的处理逻辑 - 使用特性管理系统
        if pending_level >= 9:
            # 第9关及以上的处理
            if not pending_data:
                # 新游戏：显示植物选择界面
                self.plant_selection_manager.show_plant_selection()
                self.animation_manager.reset_plant_select_animation()
                # 第9关及以上：根据关卡特性显示植物选择界面
                level_manager = LevelManager("database/levels.json")
                level_manager.start_level(pending_level)
                self.plant_selection_manager.init_plant_select_grid(level_manager)
                # 修复：只有在新游戏时才清空选中植物列表
                if not hasattr(self, '_returning_to_plant_select'):
                    self.plant_selection_manager.selected_plants_for_game = []
                    self.plant_selection_manager.flying_plants = []
                else:
                    # 清除返回标记
                    delattr(self, '_returning_to_plant_select')
            else:
                # 修复：如果是加载保存的游戏，检查植物选择状态
                plant_select_state = pending_data.get("plant_select_state", {})
                show_plant_select = plant_select_state.get("show_plant_select", False)
                selected_plants = plant_select_state.get("selected_plants_for_game", [])

                # 如果保存时正在显示植物选择但没有选择任何植物，重新初始化
                if show_plant_select and not selected_plants:
                    print("检测到空的植物选择状态，重新初始化植物选择界面")
                    self.plant_selection_manager.show_plant_selection()
                    self.animation_manager.reset_plant_select_animation()
                    level_manager = LevelManager("database/levels.json")
                    level_manager.start_level(pending_level)
                    self.plant_selection_manager.init_plant_select_grid(level_manager)
                    self.plant_selection_manager.selected_plants_for_game = []
                    self.plant_selection_manager.flying_plants = []

                    # 关键修复：确保全局植物限制设置没有被错误激活
                    # 检查数据库中是否错误地启用了global_plant_limit
                    if self.game_db and self.game_db.is_global_setting_enabled("global_plant_limit"):
                        print("警告：检测到global_plant_limit被意外启用，可能导致只显示基础植物")
                        # 可以选择自动禁用，或者给用户提示
                        # self.game_db.update_level_setting("global_plant_limit", False)
            # 注意：如果是加载保存的游戏，植物选择状态已经在 restore_game_from_save 中恢复了
        else:
            # 第8关及以下：不显示植物选择界面
            self.plant_selection_manager.hide_plant_selection()
            if not pending_data:  # 只有新游戏才清空
                self.plant_selection_manager.selected_plants_for_game = []
                self.plant_selection_manager.flying_plants = []

        # 如果显示植物选择则暂停游戏
        self.state_manager.game_paused = self.plant_selection_manager.show_plant_select

        # 清理待处理数据
        self.state_manager.clear_pending_game_data()
        if not pending_data:
            # 开始新游戏时，确保锤子冷却状态被正确初始化
            if "hammer_cooldown" not in self.game:
                self.game["hammer_cooldown"] = 0

    def manual_reload_config(self):
        """手动重新加载配置"""
        if self.state_manager.game_state == "playing":
            old_name = self.game["level_manager"].get_level_name()
            reloaded = self.game["level_manager"].reload_config()
            new_name = self.game["level_manager"].get_level_name()

            if old_name != new_name or reloaded:
                self.animation_manager.show_config_reload_notification()
                print(f"配置已重新加载：{new_name}")

    def toggle_hot_reload(self):
        """切换热重载功能"""
        self.hot_reload_enabled = not self.hot_reload_enabled
        if self.state_manager.game_state == "playing":
            self.game["level_manager"].enable_hot_reload(self.hot_reload_enabled)

        status = "已启用" if self.hot_reload_enabled else "已禁用"

    def show_config_info(self):
        """显示配置信息"""
        if self.state_manager.game_state == "playing":
            config_info = self.game["level_manager"].get_config_info()
            if config_info:
                # 新增：显示特性管理器信息
                features_info = ""
                if config_info.get("current_features"):
                    features_info = f"当前特性: {', '.join(config_info['current_features'])}"

                print("=== 关卡配置信息 ===")
                print(f"配置文件: {config_info['config_path']}")
                print(f"版本: {config_info['version']}")
                print(f"总关卡数: {config_info['total_levels']}")
                print(f"热重载: {'启用' if config_info['hot_reload'] else '禁用'}")
                if features_info:
                    print(features_info)
                print("===================")

    def reset_game_with_initialization(self, keep_level=None):
        """
        重置游戏并重新初始化所有系统（传送门、小推车等）
        修复重新开始按钮传送门消失的问题
        """
        # 使用状态管理器重置游戏
        self.game = self.state_manager.reset_game(keep_level)

        # 重新设置对象引用
        self._set_object_references()

        # 重新初始化传送门系统
        level_manager = self.game.get("level_manager")
        if level_manager:
            initialize_portal_system(self.game, level_manager)
            print(f"重置后重新初始化传送门系统，关卡: {level_manager.current_level}")

        # 重新初始化小推车系统
        self.reset_carts()

        # 重新初始化其他必要的系统
        if "hammer_cooldown" not in self.game:
            self.game["hammer_cooldown"] = 0

        # 如果是第9关及以上，重新初始化植物选择
        if level_manager and level_manager.current_level >= 9:
            # 重置植物选择状态
            self.plant_selection_manager.hide_plant_selection()
            self.plant_selection_manager.selected_plants_for_game = []
            self.plant_selection_manager.flying_plants = []

            # 如果需要显示植物选择界面
            if not hasattr(self, '_skip_plant_selection_on_reset'):
                self.plant_selection_manager.show_plant_selection()
                self.animation_manager.reset_plant_select_animation()
                self.plant_selection_manager.init_plant_select_grid(level_manager)
                self.state_manager.game_paused = True
        else:
            # 第8关及以下不显示植物选择
            self.plant_selection_manager.hide_plant_selection()
            self.plant_selection_manager.selected_plants_for_game = []
            self.plant_selection_manager.flying_plants = []
            self.state_manager.game_paused = False

    def handle_game_reset_request(self):
        """
        处理游戏重置请求（重新开始按钮、失败重置等）
        """
        if self.state_manager.game_state == "playing":
            current_level = self.game["level_manager"].current_level

            # 清除保存的游戏进度
            self.game_db.clear_saved_game(current_level)

            # 重置游戏并重新初始化所有系统
            self.reset_game_with_initialization(current_level)

            print(f"游戏已重置，关卡: {current_level}")

            return True
        return False

    def handle_game_over_reset(self):
        """
        处理游戏失败后的重置
        """
        if self.game["game_over"]:
            current_level = self.game["level_manager"].current_level

            # 清除保存的游戏进度
            self.game_db.clear_saved_game(current_level)

            # 重置游戏并重新初始化所有系统
            self.reset_game_with_initialization(current_level)

            # 重置游戏结束状态
            self.game["game_over"] = False
            self.game["game_over_sound_played"] = False

            print(f"游戏失败重置完成，关卡: {current_level}")

            return True
        return False

    def run(self):
        running = True
        while running:
            # 检查游戏状态是否改变，如果改变则切换音乐
            self.state_manager.update_game_state_music(self.music_manager)

            # 更新背景音乐管理器
            self.music_manager.update()
            self.performance_monitor.update()  # 监控性能

            # 确保音乐在播放（处理音乐自然结束的情况）
            self.music_manager.ensure_music_playing(self.state_manager.game_state)

            # 处理事件
            running = self.event_handler.handle_events()
            if not running:
                break

            # 更新游戏逻辑
            self.update_game_logic()

            # 渲染游戏
            self.renderer_manager.render_game()

            # 控制帧率
            self.clock.tick(60)

        # 程序退出前最后一次保存
        if self.state_manager.game_state == "playing" and not self.game["game_over"]:
            self.game_db.save_game_progress(self.game, self.music_manager, self)

        pygame.mixer.music.stop()
        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    game_manager = GameManager()
    game_manager.run()


if __name__ == "__main__":
    main()