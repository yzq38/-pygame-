import json
import os
import pygame


class GameDatabase:
    def __init__(self, filename="database/game_progress.json"):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        """加载游戏进度数据"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 兼容旧版本数据结构
                    if "saved_game" in data and data["saved_game"] is not None:
                        # 将旧的单一保存转换为多关卡保存格式
                        old_save = data["saved_game"]
                        level_num = old_save.get("current_level", 1)
                        data["saved_games"] = {str(level_num): old_save}
                        data["saved_game"] = None  # 清空旧格式
                    return data
            else:
                # 如果文件不存在，创建默认数据结构
                return self._create_default_data()
        except Exception as e:
            print(f"加载游戏进度数据失败: {e}")
            return self._create_default_data()

    def _create_default_data(self):
        """创建默认数据结构（简化版）"""
        return {
            "completed_levels": [],
            "level_settings": {
                "all_card_cooldown": False,
            },
            "saved_game": None,  # 保留兼容性
            "saved_games": {},  # 新的多关卡保存格式
            "coins": 0  # 全局金币数据
        }

    def save_data(self):
        """保存游戏进度数据"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存游戏进度数据失败: {e}")

    def mark_level_completed(self, level_num):
        """标记关卡为已通关"""
        if level_num not in self.data["completed_levels"]:
            self.data["completed_levels"].append(level_num)
            self.save_data()

    def is_level_completed(self, level_num):
        """检查关卡是否已通关"""
        return level_num in self.data["completed_levels"]

    def get_completed_levels(self):
        """获取所有已通关关卡"""
        return self.data["completed_levels"].copy()

    def get_completion_count(self):
        """获取已通关关卡数量"""
        return len(self.data["completed_levels"])

    def get_level_settings(self):
        """获取关卡设置（简化版）"""
        if "level_settings" not in self.data:
            self.data["level_settings"] = {}

        # 获取默认设置以确保所有新设置都存在
        default_settings = self._create_default_data()["level_settings"]

        # 合并设置，添加缺失的新设置
        for key, default_value in default_settings.items():
            if key not in self.data["level_settings"]:
                self.data["level_settings"][key] = default_value

        # 移除所有废弃的设置（清理旧配置）
        deprecated_settings = [
            "random_sun_drop", "zombie_immunity", "zombie_health_reduce",
            "global_high_armor_rate", "global_fast_zombies", "global_no_sun_drop",
            "global_plant_limit", "global_bullet_penetration", "global_plant_speed_boost",
            "global_increased_sun", "global_no_cooldown", "hardcore_mode", "speedrun_mode"
        ]

        for deprecated in deprecated_settings:
            if deprecated in self.data["level_settings"]:
                del self.data["level_settings"][deprecated]

        # 保存更新后的设置
        self.save_data()
        return self.data["level_settings"].copy()

    def update_level_setting(self, setting_key, value):
        """更新单个关卡设置（简化版）"""
        if "level_settings" not in self.data:
            self.data["level_settings"] = self._create_default_data()["level_settings"]

        # 只允许更新有效的设置
        valid_settings = ["all_card_cooldown"]

        if setting_key in valid_settings:
            self.data["level_settings"][setting_key] = value
            self.save_data()
        else:
            print(f"警告：尝试设置无效的配置项 {setting_key}")

    def reset_progress(self):
        """重置游戏进度"""
        level_settings = self.get_level_settings()  # 保留当前设置

        self.data = {
            "completed_levels": [],
            "level_settings": level_settings,
            "saved_game": None,
            "saved_games": {}  # 清空所有关卡保存
        }
        self.save_data()

    def save_game_progress(self, game_state, music_manager=None, game_manager=None):
        """保存指定关卡的游戏进度，修复樱桃炸弹等爆炸植物的保存问题"""
        try:
            # 获取当前关卡编号
            current_level = game_state["level_manager"].current_level
            level_key = str(current_level)

            # 确保saved_games字段存在
            if "saved_games" not in self.data:
                self.data["saved_games"] = {}

            # 获取音乐状态
            music_state = {}
            if music_manager:
                music_state = music_manager.get_music_state()

            # 获取植物选择状态
            plant_select_state = {}
            if game_manager:
                plant_select_state = {
                    "show_plant_select": game_manager.plant_selection_manager.show_plant_select,
                    "selected_plants_for_game": game_manager.plant_selection_manager.selected_plants_for_game.copy(),
                    "plant_select_animation_complete": game_manager.animation_manager.plant_select_animation_complete
                }

            # 获取小推车状态
            cart_data = {}
            if game_manager and hasattr(game_manager, 'cart_manager'):
                cart_data = game_manager.cart_manager.get_save_data()

            # 保存蒲公英种子数据
            dandelion_seeds_data = []
            if "dandelion_seeds" in game_state:
                for seed in game_state["dandelion_seeds"]:
                    seed_data = {
                        "start_x": seed.start_x,
                        "start_y": seed.start_y,
                        "current_x": seed.current_x,
                        "current_y": seed.current_y,
                        "target_x": seed.target_x,
                        "target_y": seed.target_y,
                        "life_time": seed.life_time,
                        "progress": seed.progress,
                        "has_hit": seed.has_hit,
                        "rotation": seed.rotation,
                        "wind_amplitude": seed.wind_amplitude,
                        "wind_frequency": seed.wind_frequency,
                        "drift_speed_x": seed.drift_speed_x,
                        "drift_speed_y": seed.drift_speed_y,
                        "rotation_speed": seed.rotation_speed,
                        "damage": getattr(seed, 'damage', 25),
                        "speed": getattr(seed, 'speed', 0.02),
                        "max_life_time": getattr(seed, 'max_life_time', 600),
                        "is_fading": getattr(seed, 'is_fading', False),
                        "fade_out_timer": getattr(seed, 'fade_out_timer', 0),
                        "fade_out_duration": getattr(seed, 'fade_out_duration', 90)
                    }
                    dandelion_seeds_data.append(seed_data)

            # 保存黄瓜效果状态
            cucumber_effects_data = {}
            if "zombie_stun_timers" in game_state:
                cucumber_effects_data["zombie_stun_timers"] = game_state["zombie_stun_timers"]
            if "cucumber_spray_timers" in game_state:
                cucumber_effects_data["cucumber_spray_timers"] = game_state["cucumber_spray_timers"]
            if "cucumber_plant_healing" in game_state:
                cucumber_effects_data["cucumber_plant_healing"] = game_state["cucumber_plant_healing"]

            # 新增：保存僵尸冰冻效果数据
            freeze_effects_data = {}
            frozen_zombies = []
            for zombie in game_state.get("zombies", []):
                if hasattr(zombie, 'is_frozen') and zombie.is_frozen:
                    frozen_zombie_data = {
                        "zombie_id": id(zombie),
                        "freeze_start_time": getattr(zombie, 'freeze_start_time', 0),
                        "original_speed": getattr(zombie, 'original_speed', zombie.base_speed),
                        "freeze_duration_remaining": 5000 - (
                                pygame.time.get_ticks() - getattr(zombie, 'freeze_start_time', 0))
                    }
                    frozen_zombies.append(frozen_zombie_data)
            freeze_effects_data["frozen_zombies"] = frozen_zombies

            # 关键修复：樱桃炸弹等爆炸植物的特殊处理
            def should_save_plant(plant):
                """判断植物是否应该被保存"""
                # 樱桃炸弹和类似的爆炸植物
                if plant.plant_type == "cherry_bomb":
                    # 检查是否已经爆炸
                    if hasattr(plant, 'has_exploded') and plant.has_exploded:
                        return False  # 已爆炸的樱桃炸弹不保存
                    if hasattr(plant, 'explosion_timer') and plant.explosion_timer > 0:
                        return False  # 正在爆炸过程中的不保存
                    if hasattr(plant, 'is_exploding') and plant.is_exploding:
                        return False  # 正在爆炸的不保存

                # 黄瓜类似处理
                elif plant.plant_type == "cucumber":
                    # 检查黄瓜是否已经触发了全屏爆炸
                    if hasattr(plant, 'has_exploded') and plant.has_exploded:
                        return False
                    if hasattr(plant, 'explosion_triggered') and plant.explosion_triggered:
                        return False

                # 其他即时爆炸类植物的处理
                elif plant.plant_type in ["potato_mine", "doom_shroom", "squash"]:
                    # 如果植物有爆炸状态标记
                    if hasattr(plant, 'has_exploded') and plant.has_exploded:
                        return False
                    if hasattr(plant, 'is_triggered') and plant.is_triggered:
                        return False

                return True  # 其他植物正常保存

            # 修复后的植物保存逻辑
            plants_data = []
            for plant in game_state["plants"]:
                if should_save_plant(plant):
                    plant_data = {
                        "row": plant.row,
                        "col": plant.col,
                        "plant_type": plant.plant_type,
                        "health": plant.health,
                        # 射击类植物参数
                        "shoot_timer": getattr(plant, 'shoot_timer', 0),
                        "current_shoot_delay": getattr(plant, 'current_shoot_delay',
                                                       plant.base_shoot_delay if hasattr(plant,
                                                                                         'base_shoot_delay') else 300),
                        "had_target_last_frame": getattr(plant, 'had_target_last_frame', False),
                        # 闪电花特殊参数
                        "lightning_timer": getattr(plant, 'lightning_timer', 0),
                        "show_lightning": getattr(plant, 'show_lightning', False),
                        "lightning_effects": getattr(plant, 'lightning_effects', []),
                        # 向日葵参数
                        "sun_timer": getattr(plant, 'sun_timer', 0) if plant.plant_type == "sunflower" else 0,
                        # 新增：爆炸植物的状态参数
                        "explosion_state": self._get_plant_explosion_state(plant)
                    }
                    plants_data.append(plant_data)

            # 保存爆炸效果数据（用于粒子系统等视觉效果的恢复）
            explosion_effects_data = []
            if "explosion_effects" in game_state:
                for effect in game_state["explosion_effects"]:
                    effect_data = {
                        "effect_type": getattr(effect, 'effect_type', 'unknown'),
                        "position": getattr(effect, 'position', (0, 0)),
                        "timer": getattr(effect, 'timer', 0),
                        "duration": getattr(effect, 'duration', 60),
                        "particles": len(getattr(effect, 'particles', []))  # 只保存粒子数量
                    }
                    explosion_effects_data.append(effect_data)

            portal_manager_data = {}
            if "portal_manager" in game_state and game_state["portal_manager"]:
                portal_manager = game_state["portal_manager"]
                portal_manager_data = {
                    "switch_timer": portal_manager.switch_timer,
                    "switch_interval": portal_manager.switch_interval,
                    "next_portal_id": portal_manager.next_portal_id,
                    "portals": []
                }

                # 保存每个传送门的状态
                for portal in portal_manager.portals:
                    portal_data = {
                        "row": portal.row,
                        "col": portal.col,
                        "portal_id": portal.portal_id,
                        "spawn_animation_timer": portal.spawn_animation_timer,
                        "despawn_animation_timer": portal.despawn_animation_timer,
                        "is_spawning": portal.is_spawning,
                        "is_despawning": portal.is_despawning,
                        "is_active": portal.is_active,
                        "rotation_angle": portal.rotation_angle,

                    }
                    portal_manager_data["portals"].append(portal_data)
            # 创建保存数据
            saved_game = {
                "sun": game_state["sun"],
                "current_level": current_level,
                "wave_mode": game_state["wave_mode"],
                "wave_timer": game_state["wave_timer"],
                "zombies_killed": game_state["zombies_killed"],
                "zombies_spawned": game_state["zombies_spawned"],
                "first_wave_spawned": game_state["first_wave_spawned"],
                "card_cooldowns": game_state.get("card_cooldowns", {}),
                "hammer_cooldown": game_state.get("hammer_cooldown", 0),
                # 传送门状态
                "portal_manager_data": portal_manager_data,
                # 关卡管理器状态
                "level_manager_state": {
                    "current_wave": game_state["level_manager"].current_wave,
                    "waves_completed": game_state["level_manager"].waves_completed,
                    "zombies_in_wave": game_state["level_manager"].zombies_in_wave,
                    "zombies_defeated": game_state["level_manager"].zombies_defeated,
                    "wave_spawned": game_state["level_manager"].wave_spawned,
                    "all_waves_completed": game_state["level_manager"].all_waves_completed,
                    "sunflower_count": game_state["level_manager"].sunflower_count,
                    "max_waves": game_state["level_manager"].max_waves,
                },

                # 植物选择状态
                "plant_select_state": plant_select_state,

                # 小推车状态
                "cart_data": cart_data,

                # 蒲公英种子状态
                "dandelion_seeds": dandelion_seeds_data,

                # 黄瓜效果状态
                "cucumber_effects": cucumber_effects_data,

                # 冰冻效果状态
                "freeze_effects": freeze_effects_data,

                # 修复后的植物信息
                "plants": plants_data,

                # 僵尸信息
                "zombies": [
                    {
                        "row": zombie.row,
                        "col": zombie.col,
                        "health": zombie.health,
                        "max_health": zombie.max_health,
                        "has_armor": zombie.has_armor,
                        "max_armor_health": zombie.max_armor_health,
                        "armor_health": zombie.armor_health,
                        "is_fast": zombie.is_fast,
                        "is_attacking": zombie.is_attacking,
                        "zombie_type": getattr(zombie, 'zombie_type', 'normal'),
                        # 巨人僵尸特有状态
                        "smash_timer": getattr(zombie, 'smash_timer', 0),
                        "has_attacked_once": getattr(zombie, 'has_attacked_once', False),
                        # 死亡动画状态
                        "is_dying": getattr(zombie, 'is_dying', False),
                        "death_animation_timer": getattr(zombie, 'death_animation_timer', 0),
                        "current_alpha": getattr(zombie, 'current_alpha', 255),
                        # 冰冻状态保存
                        "is_frozen": getattr(zombie, 'is_frozen', False),
                        "freeze_start_time": getattr(zombie, 'freeze_start_time', 0),
                        "original_speed": getattr(zombie, 'original_speed', zombie.base_speed),
                        # 眩晕和喷射状态
                        "is_stunned": getattr(zombie, 'is_stunned', False),
                        "is_spraying": getattr(zombie, 'is_spraying', False),
                        "stun_visual_timer": getattr(zombie, 'stun_visual_timer', 0)
                    }
                    for zombie in game_state["zombies"]
                ],

                # 子弹信息
                "bullets": [
                    {
                        "row": bullet.row,
                        "col": bullet.col,
                        "bullet_type": bullet.bullet_type,
                        "can_penetrate": bullet.can_penetrate,
                        "target_col": getattr(bullet, "target_col", None),
                        "speed": bullet.speed,
                        # 西瓜子弹状态
                        "start_col": getattr(bullet, "start_col", bullet.col),
                        "flight_progress": getattr(bullet, "flight_progress", 0.0),
                        "has_landed": getattr(bullet, "has_landed", False),
                        "splash_applied": getattr(bullet, "splash_applied", False),
                        "has_hit_target": getattr(bullet, "has_hit_target", False),
                        # 追踪子弹状态
                        "actual_x": getattr(bullet, "actual_x", bullet.col),
                        "actual_y": getattr(bullet, "actual_y", bullet.row),
                        "direction_x": getattr(bullet, "direction_x", 1.0),
                        "direction_y": getattr(bullet, "direction_y", 0.0),
                        "target_direction_x": getattr(bullet, "target_direction_x", 1.0),
                        "target_direction_y": getattr(bullet, "target_direction_y", 0.0),
                        "retargeting_cooldown": getattr(bullet, "retargeting_cooldown", 0),
                        # 爆炸状态
                        "explosion_triggered": getattr(bullet, "explosion_triggered", False),
                        "show_explosion": getattr(bullet, "show_explosion", False),
                        # 命中记录
                        "hit_zombies_count": len(getattr(bullet, "hit_zombies", set())),
                        "splash_hit_zombies_count": len(getattr(bullet, "splash_hit_zombies", set())),
                        # 寒冰子弹特殊属性
                        "freeze_power": getattr(bullet, "freeze_power", 5000) if bullet.bullet_type == "ice" else 0,
                        "freeze_applied_zombies": len(
                            getattr(bullet, "freeze_applied_zombies", set())) if bullet.bullet_type == "ice" else 0
                    }
                    for bullet in game_state.get("bullets", [])
                ],

                # 新增：爆炸效果数据
                "explosion_effects": explosion_effects_data,

                # 音乐状态
                "music_state": music_state,

                # 保存时间戳
                "save_time": __import__('time').time()
            }

            # 保存到指定关卡槽位
            self.data["saved_games"][level_key] = saved_game
            self.save_data()

            return True

        except Exception as e:
            print(f"保存游戏进度失败: {e}")
            return False

    def _get_plant_explosion_state(self, plant):
        """获取植物的爆炸状态信息"""
        explosion_state = {
            "has_exploded": getattr(plant, 'has_exploded', False),
            "is_exploding": getattr(plant, 'is_exploding', False),
            "explosion_timer": getattr(plant, 'explosion_timer', 0),
            "explosion_triggered": getattr(plant, 'explosion_triggered', False),
            "is_triggered": getattr(plant, 'is_triggered', False)
        }

        # 樱桃炸弹特殊状态
        if plant.plant_type == "cherry_bomb":
            explosion_state.update({
                "countdown_timer": getattr(plant, 'countdown_timer', 0),
                "explosion_radius": getattr(plant, 'explosion_radius', 1.5),
                "explosion_damage": getattr(plant, 'explosion_damage', 1000)
            })

        # 黄瓜特殊状态
        elif plant.plant_type == "cucumber":
            explosion_state.update({
                "fullscreen_explosion_triggered": getattr(plant, 'fullscreen_explosion_triggered', False),
                "stun_duration": getattr(plant, 'stun_duration', 300),
                "spray_duration": getattr(plant, 'spray_duration', 120),
                "death_probability": getattr(plant, 'death_probability', 0.5)
            })

        return explosion_state

    def has_saved_game(self, level_num=None):
        """检查是否有保存的游戏进度（可指定关卡）"""
        if "saved_games" not in self.data:
            # 检查旧格式兼容性
            return self.data.get("saved_game") is not None

        if level_num is None:
            # 检查是否有任何关卡的保存
            return len(self.data["saved_games"]) > 0
        else:
            # 检查指定关卡是否有保存
            level_key = str(level_num)
            return level_key in self.data["saved_games"]

    def get_saved_game(self, level_num=None):
        """获取保存的游戏进度（可指定关卡）"""
        if "saved_games" not in self.data:
            # 兼容旧格式
            return self.data.get("saved_game")

        if level_num is None:
            # 返回任意一个保存（用于继续游戏功能）
            if self.data["saved_games"]:
                return list(self.data["saved_games"].values())[0]
            return None
        else:
            # 返回指定关卡的保存
            level_key = str(level_num)
            return self.data["saved_games"].get(level_key)

    def clear_saved_game(self, level_num=None):
        """清除保存的游戏进度（可指定关卡）"""
        if level_num is None:
            # 清除所有保存
            self.data["saved_game"] = None
            if "saved_games" in self.data:
                self.data["saved_games"] = {}
        else:
            # 清除指定关卡的保存
            if "saved_games" in self.data:
                level_key = str(level_num)
                if level_key in self.data["saved_games"]:
                    del self.data["saved_games"][level_key]
        self.save_data()

    def get_saved_game_info(self, level_num=None):
        """获取保存游戏的基本信息（可指定关卡）"""
        saved_game = self.get_saved_game(level_num)
        if not saved_game:
            return None

        import time
        save_time = saved_game.get("save_time", 0)
        formatted_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(save_time))

        # 优先使用保存数据中的max_waves值
        current_level = saved_game["current_level"]

        # 1. 首先尝试从保存的关卡管理器状态中获取max_waves
        max_waves = None
        if "level_manager_state" in saved_game and "max_waves" in saved_game["level_manager_state"]:
            max_waves = saved_game["level_manager_state"]["max_waves"]

        # 2. 如果保存数据中没有，再从配置中获取
        if max_waves is None:
            level_configs = {
                1: {'max_waves': 3},
                2: {'max_waves': 4},
                3: {'max_waves': 4},
                4: {'max_waves': 7},
                5: {'max_waves': 4},
                6: {'max_waves': 3},
                7: {'max_waves': 3},
                8: {'max_waves': 4},
                9:{'max_waves': 3},
            }
            max_waves = level_configs.get(current_level, {}).get('max_waves', 5)  # 最后才使用默认值

        # 获取蒲公英种子和黄瓜效果信息（新增）
        dandelion_count = len(saved_game.get("dandelion_seeds", []))
        cucumber_effects_active = bool(saved_game.get("cucumber_effects", {}))

        return {
            "level": current_level,
            "save_time": formatted_time,
            "wave_mode": saved_game["wave_mode"],
            "current_wave": saved_game["level_manager_state"]["current_wave"],
            "max_waves": max_waves,  # 使用修复后的max_waves值
            "bullet_count": len(saved_game.get("bullets", [])),
            "sun": saved_game["sun"],
            "dandelion_seeds_count": dandelion_count,  # 蒲公英种子数量
            "cucumber_effects_active": cucumber_effects_active  # 黄瓜效果是否激活
        }

    def is_global_setting_enabled(self, setting_key):
        """检查全局设置是否启用特性:"""
        settings = self.get_level_settings()
        return settings.get(setting_key, False)

    def get_coins(self):
        """获取当前金币数量"""
        return self.data.get("coins", 0)

    def set_coins(self, amount):
        """设置金币数量"""
        self.data["coins"] = max(0, amount)  # 确保金币不为负数
        self.save_data()

    def add_coins(self, amount):
        """增加金币数量"""
        current_coins = self.get_coins()
        self.set_coins(current_coins + amount)

    def spend_coins(self, amount):
        """花费金币，返回是否成功"""
        current_coins = self.get_coins()
        if current_coins >= amount:
            self.set_coins(current_coins - amount)
            return True
        return False