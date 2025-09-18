"""
保存管理器 - 处理游戏进度的保存和恢复逻辑
"""
import pygame
import random
import sys
import os

# 获取当前文件所在的database目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（database的上级目录）
project_root = os.path.dirname(current_dir)
# 添加到Python路径
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.constants import get_constants
from plants import Plant
from zombies import Zombie
# 统一使用 import bullets 方式
import bullets


def auto_save_game_progress(game_db, game_state, music_manager, game_manager=None, save_interval=100):
    """自动保存游戏进度"""
    current_time = pygame.time.get_ticks()
    last_save_time = game_state.get("last_save_time", 0)

    # 每save_interval帧（默认5秒）保存一次
    if current_time - last_save_time >= save_interval * 1000 / 60:  # 转换为毫秒
        if game_state.get("wave_mode") or len(game_state.get("plants", [])) > 0:
            # 只在有意义的游戏进度时保存
            # 修改：传入 game_manager 参数
            if game_db.save_game_progress(game_state, music_manager, game_manager):
                pass
            game_state["last_save_time"] = current_time


def restore_game_from_save(saved_data, level_manager, game_manager=None):
    """从保存的数据恢复游戏状态，修复樱桃炸弹等爆炸植物的恢复问题"""
    try:
        # 创建基础游戏状态
        game = {
            "plants": [], "zombies": [], "bullets": [],
            "zombie_timer": saved_data.get("zombie_timer", 0),
            "sun": saved_data["sun"],
            "game_over": False,
            "selected": None,
            "wave_mode": saved_data["wave_mode"],
            "wave_timer": saved_data["wave_timer"],
            "zombies_spawned": saved_data["zombies_spawned"],
            "zombies_killed": saved_data["zombies_killed"],
            "first_wave_spawned": saved_data["first_wave_spawned"],
            "game_over_sound_played": False,
            "level_manager": level_manager,
            "fade_state": "none",
            "fade_alpha": 0,
            "fade_timer": 0,
            "fade_duration": 190,
            "card_cooldowns": saved_data.get("card_cooldowns", {}),
            "last_update_time": pygame.time.get_ticks(),
            "last_save_time": 0,
            "hammer_cooldown": saved_data.get("hammer_cooldown", 0),
            # 黄瓜效果状态
            "zombie_stun_timers": saved_data.get("cucumber_effects", {}).get("zombie_stun_timers", {}),
            "cucumber_spray_timers": saved_data.get("cucumber_effects", {}).get("cucumber_spray_timers", {}),
            "cucumber_plant_healing": saved_data.get("cucumber_effects", {}).get("cucumber_plant_healing", {}),
            # 新增：爆炸效果列表
            "explosion_effects": []
        }

        # 恢复植物 - 修复：正确处理爆炸植物状态
        for plant_data in saved_data.get("plants", []):
            plant = Plant(
                plant_data["row"],
                plant_data["col"],
                plant_data["plant_type"],
                get_constants(),
                None,
                level_manager
            )
            plant.health = plant_data["health"]

            # 恢复攻击型植物的射击参数
            if plant.plant_type in ["shooter", "melon_pult", "cattail", "dandelion", "lightning_flower", "ice_cactus"]:
                plant.shoot_timer = plant_data.get("shoot_timer", 0)
                plant.current_shoot_delay = plant_data.get("current_shoot_delay", plant.base_shoot_delay)
                plant.had_target_last_frame = plant_data.get("had_target_last_frame", False)

            # 恢复闪电花特殊状态
            if plant.plant_type == "lightning_flower":
                plant.lightning_timer = plant_data.get("lightning_timer", 0)
                plant.show_lightning = plant_data.get("show_lightning", False)
                plant.lightning_effects = plant_data.get("lightning_effects", [])

            # 恢复向日葵状态
            if plant.plant_type == "sunflower":
                plant.sun_timer = plant_data.get("sun_timer", 0)

            # 关键修复：恢复爆炸植物的特殊状态
            if "explosion_state" in plant_data:
                explosion_state = plant_data["explosion_state"]

                # 恢复爆炸状态属性
                for attr_name, attr_value in explosion_state.items():
                    setattr(plant, attr_name, attr_value)

                # 特殊处理：如果植物已经爆炸，不应该添加到植物列表中
                if explosion_state.get("has_exploded", False):
                    print(f"跳过已爆炸的植物: {plant.plant_type} at ({plant.row}, {plant.col})")
                    continue

                # 如果植物正在爆炸过程中，也不添加（让爆炸效果自然结束）
                if explosion_state.get("is_exploding", False):
                    print(f"跳过正在爆炸的植物: {plant.plant_type} at ({plant.row}, {plant.col})")
                    continue

            game["plants"].append(plant)

        # 恢复爆炸效果（如果有）
        if "explosion_effects" in saved_data:
            for effect_data in saved_data["explosion_effects"]:
                # 这里可以重新创建爆炸效果，或者简单跳过
                # 因为大多数情况下，玩家不会在意爆炸动画的恢复
                print(f"跳过爆炸效果恢复: {effect_data.get('effect_type', 'unknown')}")

        # 恢复僵尸 - 保持原有逻辑
        current_time = pygame.time.get_ticks()
        for zombie_data in saved_data.get("zombies", []):
            zombie_type = zombie_data.get("zombie_type", "normal")

            zombie = Zombie(
                zombie_data["row"],
                has_armor_prob=1.0 if zombie_data["has_armor"] else 0.0,
                is_fast=zombie_data["is_fast"],
                wave_mode=True,
                fast_multiplier=level_manager.get_fast_zombie_multiplier(),
                constants=get_constants(),
                sounds=None,
                images=None,
                zombie_type=zombie_type
            )

            # 恢复基本状态
            zombie.col = zombie_data["col"]
            zombie.has_armor = zombie_data["has_armor"]
            zombie.is_attacking = zombie_data["is_attacking"]
            zombie.health = zombie_data["health"]
            zombie.armor_health = zombie_data["armor_health"]

            # 恢复巨人僵尸特有状态
            if zombie_type == "giant":
                zombie.smash_timer = zombie_data.get("smash_timer", 0)
                zombie.has_attacked_once = zombie_data.get("has_attacked_once", False)

            # 恢复死亡动画状态
            zombie.is_dying = zombie_data.get("is_dying", False)
            zombie.death_animation_timer = zombie_data.get("death_animation_timer", 0)
            zombie.current_alpha = zombie_data.get("current_alpha", 255)

            # 恢复冰冻状态
            if zombie_data.get("is_frozen", False):
                zombie.is_frozen = True
                zombie.freeze_start_time = zombie_data.get("freeze_start_time", current_time)
                zombie.original_speed = zombie_data.get("original_speed", zombie.base_speed)
                freeze_elapsed = current_time - zombie.freeze_start_time
                if freeze_elapsed < 5000:
                    zombie.speed = zombie.original_speed * 0.5
                else:
                    zombie.is_frozen = False
                    zombie.speed = zombie.original_speed

            # 恢复眩晕和喷射状态
            zombie.is_stunned = zombie_data.get("is_stunned", False)
            zombie.is_spraying = zombie_data.get("is_spraying", False)
            zombie.stun_visual_timer = zombie_data.get("stun_visual_timer", 0)

            game["zombies"].append(zombie)

        # 恢复子弹状态 - 使用 bullets.create_bullet
        for bullet_data in saved_data.get("bullets", []):
            bullet = bullets.create_bullet(
                bullet_type=bullet_data["bullet_type"],
                row=bullet_data["row"],
                col=bullet_data["col"],
                can_penetrate=bullet_data["can_penetrate"],
                target_col=bullet_data.get("target_col", None),
                constants=get_constants(),
                images=None
            )

            # 恢复子弹状态...（保持原有逻辑）
            bullet.speed = bullet_data.get("speed", bullet.speed)

            if bullet.bullet_type == "ice":
                bullet.freeze_duration = bullet_data.get("freeze_power", 5000)
                bullet.freeze_applied_zombies = set()

            elif bullet.bullet_type == "melon":
                bullet.start_col = bullet_data.get("start_col", bullet.col)
                bullet.flight_progress = bullet_data.get("flight_progress", 0.0)
                bullet.has_landed = bullet_data.get("has_landed", False)
                bullet.splash_applied = bullet_data.get("splash_applied", False)
                bullet.has_hit_target = bullet_data.get("has_hit_target", False)
                bullet.explosion_triggered = bullet_data.get("explosion_triggered", False)
                bullet.show_explosion = bullet_data.get("show_explosion", False)

            elif bullet.bullet_type == "spike":
                bullet.actual_x = bullet_data.get("actual_x", bullet.col)
                bullet.actual_y = bullet_data.get("actual_y", bullet.row)
                bullet.direction_x = bullet_data.get("direction_x", 1.0)
                bullet.direction_y = bullet_data.get("direction_y", 0.0)
                bullet.target_direction_x = bullet_data.get("target_direction_x", 1.0)
                bullet.target_direction_y = bullet_data.get("target_direction_y", 0.0)
                bullet.retargeting_cooldown = bullet_data.get("retargeting_cooldown", 0)

            bullet.hit_zombies = set()
            bullet.splash_hit_zombies = set()

            game["bullets"].append(bullet)

        # 恢复其他状态...（保持原有逻辑）
        if game_manager and "plant_select_state" in saved_data:
            plant_select_state = saved_data["plant_select_state"]
            game_manager.plant_selection_manager.show_plant_select = plant_select_state.get("show_plant_select", False)
            game_manager.plant_selection_manager.selected_plants_for_game = plant_select_state.get(
                "selected_plants_for_game", [])
            game_manager.animation_manager.plant_select_animation_complete = plant_select_state.get(
                "plant_select_animation_complete", False)

        if game_manager and "cart_data" in saved_data:
            cart_data = saved_data["cart_data"]
            if cart_data:
                game_manager.cart_manager.load_save_data(cart_data)

        # 恢复蒲公英种子
        game["dandelion_seeds"] = []
        if "dandelion_seeds" in saved_data:
            for seed_data in saved_data["dandelion_seeds"]:
                seed = bullets.DandelionSeed(
                    start_x=seed_data["start_x"],
                    start_y=seed_data["start_y"],
                    target_zombie=None,
                    constants=get_constants(),
                    images=None
                )

                restore_attributes = [
                    "current_x", "current_y", "target_x", "target_y", "life_time",
                    "progress", "has_hit", "rotation", "wind_amplitude", "wind_frequency",
                    "drift_speed_x", "drift_speed_y", "rotation_speed", "is_fading",
                    "fade_out_timer", "fade_out_duration", "damage", "speed", "max_life_time"
                ]

                for attr in restore_attributes:
                    if attr in seed_data:
                        setattr(seed, attr, seed_data[attr])

                game["dandelion_seeds"].append(seed)

        # 恢复关卡管理器状态...（保持原有逻辑）
        if "level_manager_state" in saved_data:
            level_manager_state = saved_data["level_manager_state"]

            saved_wave_mode = saved_data.get("wave_mode", False)
            level_manager.wave_mode = saved_wave_mode

            level_manager.current_wave = level_manager_state.get("current_wave", 1)
            level_manager.waves_completed = level_manager_state.get("waves_completed", 0)
            level_manager.zombies_in_wave = level_manager_state.get("zombies_in_wave", 0)
            level_manager.zombies_defeated = level_manager_state.get("zombies_defeated", 0)
            level_manager.wave_spawned = level_manager_state.get("wave_spawned", False)
            level_manager.all_waves_completed = level_manager_state.get("all_waves_completed", False)
            level_manager.max_waves = level_manager_state.get("max_waves", 3)
            level_manager.sunflower_count = level_manager_state.get("sunflower_count", 0)

            if level_manager.all_waves_completed:
                level_manager.wave_mode = True

        return game

    except Exception as e:
        print(f"恢复游戏状态失败: {e}")
        return None


def create_bullet_from_save_data(bullet_data):
    """
    从保存数据创建子弹的辅助函数
    """
    # 基本参数
    base_params = {
        "bullet_type": bullet_data["bullet_type"],
        "row": bullet_data["row"],
        "col": bullet_data["col"],
        "can_penetrate": bullet_data["can_penetrate"],
        "constants": get_constants(),
        "images": None
    }

    # 添加特定类型的参数
    if bullet_data["bullet_type"] == "melon":
        base_params["target_col"] = bullet_data.get("target_col")
    elif bullet_data["bullet_type"] == "spike":
        # 尖刺子弹需要目标僵尸，但恢复时无法精确指定，设为None让其重新寻找
        base_params["target_zombie"] = None

    return bullets.create_bullet(**base_params)


def restore_dandelion_seeds_from_save(saved_seeds_data):
    """
    从保存数据恢复蒲公英种子的辅助函数
    """
    seeds = []
    for seed_data in saved_seeds_data:
        seed = bullets.DandelionSeed(
            start_x=seed_data["start_x"],
            start_y=seed_data["start_y"],
            target_zombie=None,  # 恢复时重新寻找目标
            constants=get_constants(),
            images=None
        )

        # 批量恢复属性
        for attr_name, attr_value in seed_data.items():
            if hasattr(seed, attr_name) and attr_name not in ["start_x", "start_y"]:
                setattr(seed, attr_name, attr_value)

        seeds.append(seed)

    return seeds


def check_level_has_save(game_db, level_num):
    """检查指定关卡是否有保存的进度"""
    return game_db.has_saved_game(level_num)  # 传入关卡编号


# 可选：添加一些验证函数来确保恢复的数据正确性
def validate_restored_bullet(bullet, bullet_data):
    """
    验证恢复的子弹数据是否正确
    """
    try:
        assert bullet.bullet_type == bullet_data["bullet_type"]
        assert bullet.row == bullet_data["row"]
        assert abs(bullet.col - bullet_data["col"]) < 0.01  # 浮点数比较
        assert bullet.can_penetrate == bullet_data["can_penetrate"]
        return True
    except AssertionError as e:
        print(f"子弹数据验证失败: {e}")
        return False


def validate_restored_seed(seed, seed_data):
    """
    验证恢复的蒲公英种子数据是否正确
    """
    try:
        assert abs(seed.start_x - seed_data["start_x"]) < 0.01
        assert abs(seed.start_y - seed_data["start_y"]) < 0.01
        assert abs(seed.current_x - seed_data["current_x"]) < 0.01
        assert abs(seed.current_y - seed_data["current_y"]) < 0.01
        return True
    except AssertionError as e:
        print(f"蒲公英种子数据验证失败: {e}")
        return False