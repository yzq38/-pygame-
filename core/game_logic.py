"""
游戏逻辑处理模块
"""
import pygame
import random



from .constants import *
from performance import SpatialGrid
from plants import Plant
from zombies import *
import bullets
from .cards_manager import get_available_cards_new, cards_manager
from zombies import create_zombie
import bullets
from ui.portal_manager import PortalManager

def create_zombie_for_level(row, level_manager, is_fast=False, level_settings=None):
    """根据关卡管理器创建僵尸 - 更新：使用重构后的僵尸系统"""
    # 使用关卡管理器的统一接口（内部调用特性管理器）
    armor_prob = level_manager.get_zombie_armor_prob()
    fast_multiplier = level_manager.get_fast_zombie_multiplier()

    # 检查是否是全员快速模式 - 使用特性管理系统
    if level_manager.has_all_fast_zombies():
        is_fast = True  # 强制设置为快速僵尸

    # 第13关及以后有概率生成巨人僵尸
    zombie_type = "normal"
    if level_manager.current_level >= 13:
        # 10%概率生成巨人僵尸
        if random.random() < 0.1:
            zombie_type = "giant"

    # 使用工厂方法创建僵尸
    zombie = create_zombie(
        row=row,
        zombie_type=zombie_type,
        has_armor_prob=armor_prob,
        is_fast=is_fast,
        wave_mode=True,
        fast_multiplier=fast_multiplier,
        constants=get_constants(),
        sounds=None,
        images=None,
        level_settings=level_settings
    )

    return zombie


def update_bullets(game, level_manager, level_settings=None, sounds=None):
    """优化后的子弹更新逻辑，使用 bullets 模块"""

    # 更新冰冻效果
    update_freeze_effects(game)

    # 创建空间分区并添加僵尸
    spatial_grid = SpatialGrid(GRID_WIDTH, GRID_HEIGHT)
    for zombie in game["zombies"]:
        spatial_grid.add_zombie(zombie)

    for bullet in game["bullets"][:]:
        # 更新子弹位置
        if bullet.update(game["zombies"]):
            game["bullets"].remove(bullet)
            continue

        # 检测子弹击中僵尸
        bullet_removed = False
        hit_any_zombie = False
        hit_sound_played = False

        # 根据子弹类型进行不同的处理
        if bullet.bullet_type == "melon":
            # 西瓜子弹特殊处理
            if not bullet.has_hit_target and bullet.has_landed:
                zombies_to_check = spatial_grid.get_zombies_in_row(bullet.row)
                target_zombie = None
                min_distance = float('inf')

                for zombie in zombies_to_check:
                    if bullet.can_hit_zombie(zombie):
                        distance = abs(zombie.col - bullet.col)
                        if distance < min_distance:
                            min_distance = distance
                            target_zombie = zombie

                if target_zombie:
                    attack_result = bullet.attack_zombie(target_zombie, level_settings)
                    if attack_result == 1:
                        hit_any_zombie = True
                        bullet.has_hit_target = True

                        if target_zombie.health <= 0 and not target_zombie.is_dying:
                            target_zombie.start_death_animation()

                        if sounds and sounds.get("watermelon_hit") and not hit_sound_played:
                            sounds["watermelon_hit"].play()
                            hit_sound_played = True

                        splash_count = bullet.apply_splash_damage(game["zombies"])

                        for zombie in game["zombies"]:
                            if (zombie.health <= 0 and not zombie.is_dying and
                                    id(zombie) in bullet.splash_hit_zombies):
                                zombie.start_death_animation()
                elif bullet.has_landed:
                    bullet.has_hit_target = True
                    splash_count = bullet.apply_splash_damage(game["zombies"])

        elif bullet.bullet_type == "spike":
            # 尖刺子弹的处理逻辑
            zombies_to_check = game["zombies"]

            for zombie in zombies_to_check:
                attack_result = bullet.attack_zombie(zombie, level_settings)
                if attack_result == 1:
                    hit_any_zombie = True

                    if not hit_sound_played and sounds:
                        if zombie.has_armor and zombie.armor_health > 0:
                            if sounds.get("armor_hit"):
                                sounds["armor_hit"].play()
                        else:
                            if sounds.get("zombie_hit"):
                                sounds["zombie_hit"].play()
                        hit_sound_played = True

                    if zombie.health <= 0 and not zombie.is_dying:
                        zombie.start_death_animation()

                    game["bullets"].remove(bullet)
                    bullet_removed = True
                    break

                elif attack_result == 2:  # 免疫
                    if not hit_sound_played and sounds:
                        if zombie.has_armor and zombie.armor_health > 0:
                            if sounds.get("armor_hit"):
                                sounds["armor_hit"].play()
                        else:
                            if sounds.get("zombie_hit"):
                                sounds["zombie_hit"].play()
                        hit_sound_played = True

                    game["bullets"].remove(bullet)
                    bullet_removed = True
                    break

        elif bullet.bullet_type == "ice":
            # 寒冰子弹的处理逻辑
            zombies_to_check = spatial_grid.get_zombies_in_row(bullet.row)
            for zombie in zombies_to_check:
                attack_result = bullet.attack_zombie(zombie, level_settings)
                if attack_result == 1:
                    hit_any_zombie = True
                    if not hit_sound_played and sounds:
                        if zombie.has_armor and zombie.armor_health > 0:
                            if sounds.get("armor_hit"):
                                sounds["armor_hit"].play()
                        else:
                            if sounds.get("zombie_hit"):
                                sounds["zombie_hit"].play()
                        hit_sound_played = True
                        if random.random() < 0.1:
                            if sounds.get("冻结"):
                                sounds["冻结"].play()

                    if zombie.health <= 0 and not zombie.is_dying:
                        zombie.start_death_animation()

                elif attack_result == 2:  # 免疫
                    if not hit_sound_played and sounds:
                        if zombie.has_armor and zombie.armor_health > 0:
                            if sounds.get("armor_hit"):
                                sounds["armor_hit"].play()
                        else:
                            if sounds.get("zombie_hit"):
                                sounds["zombie_hit"].play()
                        hit_sound_played = True
                        if random.random() < 0.1:
                            if sounds.get("冻结"):
                                sounds["冻结"].play()

                    if not bullet.can_penetrate:
                        game["bullets"].remove(bullet)
                        bullet_removed = True
                    break

        else:
            # 普通子弹的处理逻辑（豌豆射手）
            zombies_to_check = spatial_grid.get_zombies_in_row(bullet.row)

            for zombie in zombies_to_check:
                attack_result = bullet.attack_zombie(zombie, level_settings)
                if attack_result == 1:
                    hit_any_zombie = True

                    if not hit_sound_played and sounds:
                        if zombie.has_armor and zombie.armor_health > 0:
                            if sounds.get("armor_hit"):
                                sounds["armor_hit"].play()
                        else:
                            if sounds.get("zombie_hit"):
                                sounds["zombie_hit"].play()
                        hit_sound_played = True

                    if zombie.health <= 0 and not zombie.is_dying:
                        zombie.start_death_animation()

                    if not bullet.can_penetrate:
                        game["bullets"].remove(bullet)
                        bullet_removed = True
                        break
                    break

                elif attack_result == 2:  # 免疫
                    if not hit_sound_played and sounds:
                        if zombie.has_armor and zombie.armor_health > 0:
                            if sounds.get("armor_hit"):
                                sounds["armor_hit"].play()
                        else:
                            if sounds.get("zombie_hit"):
                                sounds["zombie_hit"].play()
                        hit_sound_played = True

                    if not bullet.can_penetrate:
                        game["bullets"].remove(bullet)
                        bullet_removed = True
                    break

        if bullet_removed:
            continue

        # 更新西瓜爆炸粒子效果
        if bullet.bullet_type == "melon" and bullet.show_explosion:
            bullet.update_explosion_particles()

        # 检查西瓜子弹是否应该被移除
        if (bullet.bullet_type == "melon" and bullet.has_hit_target and
                not bullet.show_explosion and bullet in game["bullets"]):
            game["bullets"].remove(bullet)


def update_plant_shooting(game, level_manager, sounds=None):
    """更新植物射击逻辑 - 支持传送门穿越"""

    # 获取传送门管理器
    portal_manager = game.get("portal_manager")

    def has_zombie_in_row_ahead(plant, zombies):
        """检测植物前方是否有僵尸，考虑传送门逻辑"""
        return has_zombie_in_row_ahead_with_portal(plant, zombies, portal_manager)

    def has_any_zombie_on_map(zombies):
        return len(zombies) > 0

    def find_nearest_zombie_in_row(plant, zombies):
        """寻找行内最近的僵尸，考虑传送门逻辑"""
        return find_nearest_zombie_with_portal(plant, zombies, portal_manager)

    for plant in game["plants"]:
        update_result = plant.update()

        # 处理向日葵产生阳光
        if isinstance(update_result, int) and update_result > 0:
            game["sun"] = add_sun_safely(game["sun"], update_result)

        # 检测是否有新僵尸波次出现
        if plant.plant_type in ["shooter", "melon_pult", "cattail", "dandelion", "lightning_flower", "ice_cactus"]:
            if plant.plant_type == "cattail":
                has_target = has_any_zombie_on_map(game["zombies"])
            elif plant.plant_type in ["dandelion", "lightning_flower"]:
                has_target = has_any_zombie_on_map(game["zombies"])
            elif plant.plant_type == "ice_cactus":
                has_target = has_zombie_in_row_ahead(plant, game["zombies"])
            else:
                has_target = has_zombie_in_row_ahead(plant, game["zombies"])
            plant.check_for_new_wave(has_target)

        # 射击逻辑
        if plant.can_shoot():
            should_shoot = False
            target_zombie = None

            if plant.plant_type == "cattail":
                if has_any_zombie_on_map(game["zombies"]):
                    target_zombie = plant.find_nearest_zombie(game["zombies"])
                    should_shoot = target_zombie is not None
            elif plant.plant_type in ["dandelion", "lightning_flower"]:
                if has_any_zombie_on_map(game["zombies"]):
                    should_shoot = True
            elif plant.plant_type in ["shooter", "melon_pult"]:
                should_shoot = has_zombie_in_row_ahead(plant, game["zombies"])
            elif plant.plant_type == "ice_cactus":
                should_shoot = has_zombie_in_row_ahead(plant, game["zombies"])

            if should_shoot:
                bullet = None

                # 使用 bullets.create_bullet 工厂函数，修复：直接传递传送门参数
                if plant.plant_type == "melon_pult":
                    # 西瓜投手：创建西瓜子弹，考虑传送门目标
                    target_col = get_bullet_target_col_with_portal(plant, game["zombies"], portal_manager)

                    bullet = bullets.create_bullet(
                        bullet_type="melon",
                        row=plant.row,
                        col=plant.col + 0.5,
                        target_col=target_col,
                        constants=get_constants(),
                        images=None
                    )

                elif plant.plant_type == "cattail":
                    # 猫尾草：创建追踪尖刺子弹
                    bullet = bullets.create_bullet(
                        bullet_type="spike",
                        row=plant.row,
                        col=plant.col + 0.5,
                        target_zombie=target_zombie,
                        constants=get_constants(),
                        images=None
                    )

                elif plant.plant_type == "dandelion":
                    # 蒲公英：创建飘散种子（特殊处理）
                    seeds = plant.create_dandelion_seeds(game["zombies"])
                    if "dandelion_seeds" not in game:
                        game["dandelion_seeds"] = []
                    game["dandelion_seeds"].extend(seeds)

                    if sounds and sounds.get("dandelion_shoot"):
                        sounds["dandelion_shoot"].play()

                elif plant.plant_type == "lightning_flower":
                    # 闪电花：执行链式攻击
                    zombies_hit = plant.perform_lightning_attack(game["zombies"], sounds)
                    if zombies_hit > 0:
                        if sounds and sounds.get("lightning_flower"):
                            sounds["lightning_flower"].play()

                elif plant.plant_type == "ice_cactus":
                    # 寒冰仙人掌：创建寒冰穿透子弹，支持传送门穿越
                    bullet = bullets.create_bullet(
                        bullet_type="ice",
                        row=plant.row,
                        col=plant.col + 0.5,
                        can_penetrate=True,
                        constants=get_constants(),
                        images=None,
                        portal_manager=portal_manager,
                        source_plant_row=plant.row,
                        source_plant_col=plant.col
                    )

                    if sounds and sounds.get("ice_cactus_shoot"):
                        sounds["ice_cactus_shoot"].play()

                else:
                    # 豌豆射手：创建普通子弹，支持传送门穿越
                    can_penetrate = level_manager.has_bullet_penetration()
                    random_penetration_prob = level_manager.get_random_penetration_prob()
                    if random_penetration_prob > 0 and random.random() < random_penetration_prob:
                        can_penetrate = True

                    bullet = bullets.create_bullet(
                        bullet_type="pea",
                        row=plant.row,
                        col=plant.col + 0.5,
                        can_penetrate=can_penetrate,
                        constants=get_constants(),
                        images=None,
                        portal_manager=portal_manager,
                        source_plant_row=plant.row,
                        source_plant_col=plant.col
                    )

                # 将子弹添加到游戏状态
                if bullet:
                    game["bullets"].append(bullet)

                plant.reset_shoot_timer()

def update_dandelion_seeds(game, level_manager, level_settings=None, sounds=None):
    """更新蒲公英种子状态和碰撞检测 - 使用 bullets 模块"""
    if "dandelion_seeds" not in game:
        game["dandelion_seeds"] = []
        return

    for seed in game["dandelion_seeds"][:]:
        # 更新种子位置
        if seed.update(game["zombies"]):
            game["dandelion_seeds"].remove(seed)
            continue

        # 检测种子击中僵尸
        hit_any_zombie = False
        for zombie in game["zombies"][:]:
            if seed.attack_zombie(zombie):
                hit_any_zombie = True

                # 播放击中音效
                if sounds:
                    if zombie.has_armor and zombie.armor_health > 0:
                        if sounds.get("armor_hit"):
                            sounds["armor_hit"].play()
                    else:
                        if sounds.get("zombie_hit"):
                            sounds["zombie_hit"].play()

                # 检查僵尸是否需要开始死亡动画
                if zombie.health <= 0 and not zombie.is_dying:
                    zombie.start_death_animation()

                # 种子击中后移除
                if seed in game["dandelion_seeds"]:
                    game["dandelion_seeds"].remove(seed)
                break

def update_hammer_cooldown(game):
    """更新锤子冷却时间"""
    if "hammer_cooldown" in game and game["hammer_cooldown"] > 0:
        game["hammer_cooldown"] -= 1
        if game["hammer_cooldown"] <= 0:
            game["hammer_cooldown"] = 0

def handle_plant_placement(game, cards, x, y, level_manager, level_settings=None, sounds=None, state_manager=None):
    """处理植物种植逻辑，使用统一的卡牌冷却管理 - 更新：使用特性管理系统，修复：种植时立即清除预览"""
    adj_x = x - BATTLEFIELD_LEFT
    adj_y = y - BATTLEFIELD_TOP

    if 0 <= adj_x < total_battlefield_width and 0 <= adj_y < total_battlefield_height:
        # 计算点击的网格坐标
        col = 0
        while col < GRID_WIDTH and adj_x > (col + 1) * GRID_SIZE + col * GRID_GAP:
            col += 1
        row = 0
        while row < GRID_HEIGHT and adj_y > (row + 1) * GRID_SIZE + row * GRID_GAP:
            row += 1
        # 检查传送门占用情况
        if "portal_manager" in game and game["portal_manager"]:
            portal_manager = game["portal_manager"]
            if not portal_manager.can_place_plant_at(row, col):
                # 传送门位置不能放置植物，显示提示或播放错误音效
                if sounds and sounds.get("plant_place_fail"):
                    sounds["plant_place_fail"].play()
                return False

        # 找到该位置的植物（如有）
        target_plant = None
        for p in game["plants"]:
            if p.row == row and p.col == col:
                target_plant = p
                break

        # 铲子模式：移除植物
        if game["selected"] == "shovel" and target_plant:
            if target_plant.plant_type == "sunflower":
                level_manager.remove_sunflower()
            game["plants"].remove(target_plant)

            # 立即清除植物预览
            if state_manager:
                state_manager.clear_plant_preview()

            return True
        # 锤子模式：杀死该格子内的所有僵尸
        elif game["selected"] == "hammer":
            # 检查锤子冷却状态
            hammer_cooldown = game.get("hammer_cooldown", 0)
            if hammer_cooldown > 0:
                return False

            # 杀死指定格子内的所有僵尸（改进的碰撞检测）
            zombies_killed = 0
            for zombie in game["zombies"][:]:  # 使用切片复制避免迭代时修改列表
                # 检查僵尸是否在目标格子内（改进的检测逻辑）
                zombie_row = int(zombie.row)

                # 只检查同一行的僵尸
                if zombie_row == row:
                    # 计算僵尸的实际占用范围
                    zombie_size = getattr(zombie, 'size_multiplier', 1.0)  # 获取僵尸大小倍数
                    zombie_left = zombie.col  # 僵尸左边界
                    zombie_right = zombie.col + zombie_size  # 僵尸右边界
                    zombie_center = zombie.col + zombie_size / 2  # 僵尸中心点

                    # 格子的范围
                    grid_left = col
                    grid_right = col + 1

                    # 计算重叠范围
                    overlap_left = max(zombie_left, grid_left)
                    overlap_right = min(zombie_right, grid_right)
                    overlap_length = max(0, overlap_right - overlap_left)

                    # 判断条件：僵尸的四分之一以上在格子内，或者僵尸中心在格子内
                    zombie_quarter_size = zombie_size / 4
                    is_quarter_inside = overlap_length >= zombie_quarter_size
                    is_center_inside = grid_left <= zombie_center <= grid_right

                    # 如果满足任一条件，则杀死僵尸
                    if is_quarter_inside or is_center_inside:
                        # 杀死僵尸
                        game["zombies"].remove(zombie)
                        zombies_killed += 1

                        # 更新击杀计数器（只在非波次模式下计算）
                        if not game.get("wave_mode", False):
                            game["zombies_killed"] += 1

                        # 处理阳光掉落
                        should_drop_sun = True
                        if game.get("wave_mode", False):
                            level_mgr = game.get("level_manager")
                            if level_mgr and level_mgr.no_sun_drop_in_wave_mode():
                                should_drop_sun = False

                        if should_drop_sun:
                            level_mgr = game.get("level_manager")
                            if level_mgr and level_mgr.has_special_feature("random_sun_drop"):
                                # 随机掉落5或10阳光
                                sun_amount = random.choice([5, 10])
                                game["sun"] = add_sun_safely(game["sun"], sun_amount)
                            else:
                                # 默认掉落20阳光
                                game["sun"] = add_sun_safely(game["sun"], 15)

                        # 处理金币掉落
                        if hasattr(game, '_game_manager') and game['_game_manager']:
                            game['_game_manager']._handle_coin_drop()
                        else:
                            # 如果无法访问game_manager，直接在这里实现金币掉落逻辑
                            coin_drop_chance = random.random()
                            coins_to_add = 0
                            if coin_drop_chance < 0.01:  # 1%概率掉落10￥
                                coins_to_add = 10
                            elif coin_drop_chance < 0.05:  # 5%概率掉落5￥
                                coins_to_add = 5
                            elif coin_drop_chance < 0.10:  # 10%概率掉落1￥
                                coins_to_add = 1

                            # 将金币数量存储到游戏状态中，稍后同步到game_manager
                            if coins_to_add > 0:
                                if '_pending_coins' not in game:
                                    game['_pending_coins'] = 0
                                game['_pending_coins'] += coins_to_add

                        # 重要：如果在波次模式下，需要更新波次进度
                        if game.get("wave_mode", False):
                            level_mgr = game.get("level_manager")
                            if level_mgr:
                                level_mgr.zombie_defeated()

            # 如果杀死了僵尸，播放音效并设置冷却时间
            if zombies_killed > 0:
                # 播放锤子音效
                if sounds and sounds.get("hammer_hit"):
                    sounds["hammer_hit"].play()

                # 设置锤子冷却时间（20秒）
                game["hammer_cooldown"] = HAMMER_COOLDOWN_TIME

                # 清除选择状态
                game["selected"] = None

                # 清除植物预览
                if state_manager:
                    state_manager.clear_plant_preview()

                print(f"锤子击杀了 {zombies_killed} 只僵尸！")
                return True
            else:
                print("该格子内没有僵尸可以击杀")
                return False

        # 植物模式：放置植物
        elif game["selected"] in [c["type"] for c in cards]:
            selected_card = next(c for c in cards if c["type"] == game["selected"])

            # 使用统一的卡牌管理器检查冷却时间 - 更新：使用特性管理系统
            cooldown_active = False

            # 检查是否需要冷却（第八关或关卡特殊设置） - 使用特性管理系统
            if (level_manager.has_card_cooldown() or
                    (level_settings and level_settings.get("all_card_cooldown", False)) or
                    level_manager.current_level == 8):  # 第八关强制启用冷却

                if game["selected"] in game["card_cooldowns"]:
                    if game["card_cooldowns"][game["selected"]] > 0:
                        cooldown_active = True

            if cooldown_active:
                return False  # 卡牌还在冷却中，不能使用
            # 如果该位置有不满血坚果墙，则可以修复
            if game["selected"] == "wall_nut":
                if (target_plant and
                        target_plant.plant_type == "wall_nut" and
                        target_plant.health < target_plant.max_health):

                    # 修复坚果墙到满血
                    target_plant.health = target_plant.max_health

                    # 扣除阳光（修复成本可以和种植成本相同或更低）
                    selected_card = next(c for c in cards if c["type"] == "wall_nut")
                    repair_cost = selected_card["cost"]  # 或者设置更低的修复成本，比如 repair_cost = selected_card["cost"] // 2

                    if game["sun"] >= repair_cost:
                        game["sun"] -= repair_cost

                        # 播放音效
                        if sounds and sounds.get("plant_place"):
                            sounds["plant_place"].play()

                        # 设置卡牌冷却（如果启用）
                        if (level_manager.has_card_cooldown() or
                                (level_settings and level_settings.get("all_card_cooldown", False)) or
                                level_manager.current_level == 8):
                            cooldown_time = cards_manager.get_card_cooldown_time("wall_nut", level_manager)
                            game["card_cooldowns"]["wall_nut"] = cooldown_time

                        # 立即清除植物预览
                        if state_manager:
                            state_manager.clear_plant_preview()

                        return True
                    else:
                        return False  # 阳光不足，无法修复
            # 检查位置是否为空且阳光足够
            if not target_plant and game["sun"] >= selected_card["cost"]:
                # 特殊检查：向日葵限制 - 使用特性管理系统
                if game["selected"] == "sunflower":
                    if not level_manager.can_plant_sunflower():
                        return False  # 不能种植向日葵
                    level_manager.plant_sunflower()

                # 种植植物
                plant_type = game["selected"]
                if plant_type == "melon_pult":
                    plant_type = "melon_pult"
                elif plant_type == "cattail":
                    plant_type = "cattail"
                elif plant_type == "wall_nut":
                    plant_type = "wall_nut"
                elif plant_type == "cucumber":
                    plant_type = "cucumber"

                plant = Plant(row, col, plant_type, get_constants(), None, game["level_manager"])
                game["plants"].append(plant)
                game["sun"] -= selected_card["cost"]

                # 使用统一的卡牌管理器设置冷却时间 - 使用特性管理系统
                if (level_manager.has_card_cooldown() or
                        (level_settings and level_settings.get("all_card_cooldown", False)) or
                        level_manager.current_level == 8):  # 第八关强制启用冷却

                    # 使用卡牌管理器获取统一的冷却时间（包括第八关+1秒处理）
                    cooldown_time = cards_manager.get_card_cooldown_time(game["selected"], level_manager)
                    game["card_cooldowns"][game["selected"]] = cooldown_time

                # 播放种植音效
                if sounds and sounds.get("plant_place"):
                    sounds["plant_place"].play()

                # 关键修复：种植成功后立即清除植物预览
                if state_manager:
                    state_manager.clear_plant_preview()

                return True

    return False


def initialize_portal_system(game_state, level_manager):
    """初始化传送门系统 - 基于特性管理器的修复版本"""
    should_have_portals = False

    if level_manager:
        current_level = level_manager.current_level

        # 直接从特性管理器获取该关卡的推荐特性
        from core.features_manager import features_manager
        recommended_features = features_manager.get_recommended_features_for_level(current_level)

        # 检查推荐特性中是否包含传送门系统
        if "portal_system" in recommended_features:
            should_have_portals = True
            print(f"关卡 {current_level} 的推荐特性包含传送门系统")

        # 备选方案：也检查level_manager的特性配置
        elif hasattr(level_manager, 'has_special_feature') and level_manager.has_special_feature("portal_system"):
            should_have_portals = True
            print(f"关卡 {current_level} 通过level_manager配置了传送门系统")

    if should_have_portals:
        # 获取传送门系统的配置参数
        from core.features_manager import features_manager
        portal_feature = features_manager.get_feature("portal_system")
        portal_config = portal_feature.default_value if portal_feature else {}

        # 创建传送门管理器
        from ui.portal_manager import PortalManager
        portal_manager = PortalManager(level_manager, auto_initialize=True)

        # 应用特性管理器中的配置（如果需要的话）
        if portal_config:
            portal_manager.switch_interval = portal_config.get("switch_interval", 20) * 60  # 转换为帧数
            # 可以根据需要应用更多配置

        game_state["portal_manager"] = portal_manager

    else:
        game_state["portal_manager"] = None
        if level_manager:
            pass


def update_portal_system(game):
    """更新传送门系统"""
    if "portal_manager" in game and game["portal_manager"]:
        game["portal_manager"].update()



def update_zombie_portal_interaction(game):
    """更新僵尸与传送门的交互"""
    if "portal_manager" not in game or not game["portal_manager"]:
        return

    portal_manager = game["portal_manager"]

    # 检查每个僵尸是否经过传送门
    for zombie in game["zombies"][:]:
        # 检查僵尸当前位置是否有传送门
        portal = portal_manager.get_portal_at_position(int(zombie.row), int(zombie.col))
        if portal and portal.is_active:
            # 30%概率传送僵尸
            if random.random() < 0.3:  # 可以从特性配置中读取这个概率传送门系统已激活
                success = portal_manager.teleport_zombie(zombie)
                if success:
                    pass

def spawn_zombie_wave_fixed(game_state, first_wave=False, zombies_per_row=None, sounds=None):
    """修复后的生成僵尸波次函数，准确计算僵尸数量并使用关卡配置 - 更新：使用特性管理系统"""
    # 第一波僵尸播放预警音效
    if first_wave and sounds and sounds.get("wave_warning"):
        sounds["wave_warning"].play()  # 普通播放，不暂停背景音乐

    if zombies_per_row is None:
        zombies_per_row = [random.randint(3, 4) for _ in range(GRID_HEIGHT)]

    # 获取关卡管理器
    level_manager = game_state.get("level_manager")
    if not level_manager:
        # 如果没有关卡管理器，使用默认值
        armor_prob = 0.5
        fast_multiplier = 2.5
        all_fast = False
    else:
        # 从关卡管理器获取配置 - 使用特性管理系统
        armor_prob = level_manager.get_zombie_armor_prob()
        fast_multiplier = level_manager.get_fast_zombie_multiplier()
        all_fast = level_manager.has_all_fast_zombies()  # 检查是否全员快速

    for row in range(GRID_HEIGHT):
        # 每行生成指定数量的僵尸
        zombie_count = zombies_per_row[row]
        # 如果是全员快速模式，所有僵尸都是快速的；否则随机选择一个位置作为快速僵尸
        if all_fast:
            fast_zombie_indices = list(range(zombie_count))  # 所有僵尸都快速
        else:
            fast_zombie_indices = [random.randint(0, zombie_count - 1)] if zombie_count > 0 else []

        for i in range(zombie_count):
            # 每个僵尸之间有间隔，避免重叠
            spawn_delay = i * 30  # 每个僵尸间隔30帧生成

            # 使用关卡配置的铁甲概率（而不是硬编码50%）
            has_armor = random.random() < armor_prob

            # 当前是否为快速僵尸
            is_fast = (i in fast_zombie_indices)

            # 确定僵尸类型 - 新增：第13关及以后有概率生成巨人僵尸
            zombie_type = "normal"
            if level_manager and level_manager.current_level >= 13:
                # 10%概率生成巨人僵尸
                if random.random() < 0.1:
                    zombie_type = "giant"

            # 创建僵尸，传入波次模式和是否为快速僵尸参数
            zombie = create_zombie(
                row=row,
                zombie_type=zombie_type,
                has_armor_prob=1.0 if has_armor else 0.0,
                is_fast=is_fast,
                wave_mode=True,
                fast_multiplier=fast_multiplier,
                constants=get_constants(),
                sounds=sounds,
                images=None,
                level_settings=None
            )

            # 稍微错开一点位置，避免完全重叠
            zombie.col += i * 0.3
            game_state["zombies"].append(zombie)


def update_card_cooldowns(game):
    """更新卡牌冷却时间"""
    if "card_cooldowns" in game:
        for card_type in list(game["card_cooldowns"].keys()):
            if game["card_cooldowns"][card_type] > 0:
                game["card_cooldowns"][card_type] -= 1
            else:
                # 冷却完成，移除记录
                del game["card_cooldowns"][card_type]


def handle_cucumber_fullscreen_explosion(game, cucumber_explosion_data, sounds=None):
    """
    处理黄瓜的全屏爆炸效果 - 改进植物治疗逻辑
    """
    if not cucumber_explosion_data:
        return

    stun_duration = cucumber_explosion_data['stun_duration']
    spray_duration = cucumber_explosion_data['spray_duration']
    death_probability = cucumber_explosion_data['death_probability']
    plant_row = cucumber_explosion_data['plant_row']
    plant_col = cucumber_explosion_data['plant_col']

    # 播放黄瓜爆炸音效
    if sounds and sounds.get("cucumber_explosion"):
        sounds["cucumber_explosion"].play()

    # 确保游戏状态有必要的字典
    if "zombie_stun_timers" not in game:
        game["zombie_stun_timers"] = {}
    if "cucumber_spray_timers" not in game:
        game["cucumber_spray_timers"] = {}

    # 第一步：对所有僵尸应用眩晕和喷射效果
    for zombie in game["zombies"]:
        zombie_id = id(zombie)

        # 检查僵尸是否已经冰冻，如果是则保存冰冻状态
        was_frozen = hasattr(zombie, 'is_frozen') and zombie.is_frozen
        original_speed = getattr(zombie, 'original_speed', None)
        freeze_start_time = getattr(zombie, 'freeze_start_time', None)

        # 1. 应用眩晕效果（5秒）
        game["zombie_stun_timers"][zombie_id] = stun_duration

        # 2. 设置喷射计时器（2秒）
        game["cucumber_spray_timers"][zombie_id] = spray_duration

        # 3. 50%概率在喷射后死亡（延迟执行）
        if random.random() < death_probability:
            if not hasattr(zombie, 'cucumber_marked_for_death'):
                zombie.cucumber_marked_for_death = True

        # 恢复冰冻状态（如果之前是冰冻的）
        if was_frozen:
            zombie.is_frozen = True
            if original_speed is not None:
                zombie.original_speed = original_speed
            if freeze_start_time is not None:
                zombie.freeze_start_time = freeze_start_time

    # 治疗所有受伤的植物
    plants_to_heal = 0
    for plant in game["plants"]:
        if plant.health < plant.max_health:
            plants_to_heal += 1

    # 创建植物治疗记录，用于持续治疗（所有植物，不管是否受伤）
    if "cucumber_plant_healing" not in game:
        game["cucumber_plant_healing"] = {}

    # 记录需要持续治疗的植物位置（所有植物）
    for plant in game["plants"]:
        plant_key = f"{plant.row}_{plant.col}"
        game["cucumber_plant_healing"][plant_key] = spray_duration


def update_cucumber_effects(game, sounds=None):
    """
    更新黄瓜效果状态 - 改进持续治疗效果
    """
    if "zombie_stun_timers" not in game:
        game["zombie_stun_timers"] = {}
    if "cucumber_spray_timers" not in game:
        game["cucumber_spray_timers"] = {}
    if "cucumber_plant_healing" not in game:
        game["cucumber_plant_healing"] = {}

    # 更新眩晕计时器
    stun_timers_to_remove = []
    for zombie_id, timer in game["zombie_stun_timers"].items():
        game["zombie_stun_timers"][zombie_id] = timer - 1
        if game["zombie_stun_timers"][zombie_id] <= 0:
            stun_timers_to_remove.append(zombie_id)

    # 移除已经结束的眩晕效果
    for zombie_id in stun_timers_to_remove:
        del game["zombie_stun_timers"][zombie_id]

    healing_to_remove = []
    for plant_key, timer in game["cucumber_plant_healing"].items():
        game["cucumber_plant_healing"][plant_key] = timer - 1

        # 每20帧治疗一次植物
        if timer % 20 == 0:
            row_str, col_str = plant_key.split('_')
            row, col = int(row_str), int(col_str)

            # 查找并治疗植物
            for plant in game["plants"]:
                if plant.row == row and plant.col == col:
                    if plant.health < plant.max_health:
                        old_health = plant.health
                        # 每次治疗50点血量
                        heal_amount = min(50, plant.max_health - plant.health)
                        plant.health = min(plant.max_health, plant.health + heal_amount)

                        # 计算治疗进度
                        health_percentage = (plant.health / plant.max_health) * 100

                    break

        if game["cucumber_plant_healing"][plant_key] <= 0:
            healing_to_remove.append(plant_key)

    # 移除已经结束的治疗效果
    for plant_key in healing_to_remove:
        del game["cucumber_plant_healing"][plant_key]

    # 更新喷射计时器
    spray_timers_to_remove = []
    zombies_to_remove = []

    for zombie_id, timer in game["cucumber_spray_timers"].items():
        game["cucumber_spray_timers"][zombie_id] = timer - 1

        # 喷射结束时检查是否需要死亡
        if game["cucumber_spray_timers"][zombie_id] <= 0:
            spray_timers_to_remove.append(zombie_id)

            # 查找对应的僵尸对象
            for zombie in game["zombies"]:
                if id(zombie) == zombie_id:
                    if hasattr(zombie, 'cucumber_marked_for_death') and zombie.cucumber_marked_for_death:
                        zombies_to_remove.append(zombie)
                    break

    # 移除已经结束的喷射效果
    for zombie_id in spray_timers_to_remove:
        del game["cucumber_spray_timers"][zombie_id]

    # 移除标记死亡的僵尸
    for zombie in zombies_to_remove:
        if zombie in game["zombies"]:
            # 在移除僵尸前检查是否处于冰冻状态
            was_frozen = hasattr(zombie, 'is_frozen') and zombie.is_frozen

            game["zombies"].remove(zombie)

            # 更新击杀计数器（只在非波次模式下计算）
            if not game.get("wave_mode", False):
                game["zombies_killed"] += 1

            # 处理阳光掉落
            should_drop_sun = True
            if game.get("wave_mode", False):
                level_mgr = game.get("level_manager")
                if level_mgr and level_mgr.no_sun_drop_in_wave_mode():
                    should_drop_sun = False

            if should_drop_sun:
                level_mgr = game.get("level_manager")
                if level_mgr and level_mgr.has_special_feature("random_sun_drop"):
                    # 随机掉落5或10阳光
                    sun_amount = random.choice([5, 10])
                    game["sun"] = add_sun_safely(game["sun"], sun_amount)
                else:
                    # 默认掉落20阳光
                    game["sun"] = add_sun_safely(game["sun"], 15)

            if hasattr(game, '_game_manager') and game['_game_manager']:
                game['_game_manager']._handle_coin_drop()
            else:
                # 如果无法访问game_manager，直接在这里实现金币掉落逻辑
                coin_drop_chance = random.random()
                coins_to_add = 0
                if coin_drop_chance < 0.01:  # 1%概率掉落10￥
                    coins_to_add = 10
                elif coin_drop_chance < 0.05:  # 5%概率掉落5￥
                    coins_to_add = 5
                elif coin_drop_chance < 0.10:  # 10%概率掉落1￥
                    coins_to_add = 1

                # 将金币数量存储到游戏状态中，稍后同步到game_manager
                if coins_to_add > 0:
                    if '_pending_coins' not in game:
                        game['_pending_coins'] = 0
                    game['_pending_coins'] += coins_to_add

            # 重要：如果在波次模式下，需要更新波次进度
            if game.get("wave_mode", False):
                level_mgr = game.get("level_manager")
                if level_mgr:
                    level_mgr.zombie_defeated()


def update_freeze_effects(game):
    """更新所有僵尸的冰冻效果 """
    current_time = pygame.time.get_ticks()
    freeze_duration = 5000  # 5秒 = 5000毫秒

    for zombie in game["zombies"]:
        if hasattr(zombie, 'is_frozen') and zombie.is_frozen:
            # 检查冰冻是否过期
            time_frozen = current_time - zombie.freeze_start_time

            if time_frozen >= freeze_duration:
                # 解除冰冻
                zombie.is_frozen = False
                if hasattr(zombie, 'original_speed'):
                    zombie.speed = zombie.original_speed
                    print(f"僵尸冰冻效果结束，速度恢复到 {zombie.speed}")
                    del zombie.original_speed
                if hasattr(zombie, 'freeze_start_time'):
                    del zombie.freeze_start_time



def is_zombie_stunned(game, zombie):
    """
    检查僵尸是否处于眩晕状态

    Args:
        game: 游戏状态字典
        zombie: 僵尸对象

    Returns:
        bool: 是否眩晕
    """
    if "zombie_stun_timers" not in game:
        return False

    zombie_id = id(zombie)
    return zombie_id in game["zombie_stun_timers"] and game["zombie_stun_timers"][zombie_id] > 0


def is_zombie_spraying(game, zombie):
    """
    检查僵尸是否正在喷射

    Args:
        game: 游戏状态字典
        zombie: 僵尸对象

    Returns:
        bool: 是否正在喷射
    """
    if "cucumber_spray_timers" not in game:
        return False

    zombie_id = id(zombie)
    return zombie_id in game["cucumber_spray_timers"] and game["cucumber_spray_timers"][zombie_id] > 0

def add_sun_safely(current_sun, amount):
    """安全地增加阳光，避免超过上限"""
    MAX_SUN = 1000  # 最大阳光数量
    new_sun = current_sun + amount
    if new_sun > MAX_SUN:
        return MAX_SUN
    return new_sun


def has_zombie_in_row_ahead_with_portal(plant, zombies, portal_manager):
    """检测植物前方是否有僵尸，考虑传送门穿越逻辑"""
    if not portal_manager:
        return _has_zombie_in_row_ahead_normal(plant, zombies)

    plant_row_portals = _get_portals_in_row(portal_manager, plant.row)

    if not plant_row_portals:
        return _has_zombie_in_row_ahead_normal(plant, zombies)

    nearest_portal = _find_nearest_portal_to_right(plant, plant_row_portals)

    if not nearest_portal:
        return _has_zombie_in_row_ahead_normal(plant, zombies)

    # 检查传送门左侧是否有僵尸
    has_zombie_before_portal = _has_zombie_between_positions(
        zombies, plant.row, plant.col, nearest_portal.col
    )

    if has_zombie_before_portal:
        return True

    # 检查其他传送门出口是否有僵尸
    return _has_zombie_at_portal_exits(zombies, portal_manager, nearest_portal)


def find_nearest_zombie_with_portal(plant, zombies, portal_manager):
    """寻找最近的僵尸，考虑传送门穿越逻辑"""
    if not portal_manager:
        return _find_nearest_zombie_normal(plant, zombies)

    plant_row_portals = _get_portals_in_row(portal_manager, plant.row)

    if not plant_row_portals:
        return _find_nearest_zombie_normal(plant, zombies)

    nearest_portal = _find_nearest_portal_to_right(plant, plant_row_portals)

    if not nearest_portal:
        return _find_nearest_zombie_normal(plant, zombies)

    # 优先攻击传送门左侧的僵尸
    nearest_before_portal = _find_nearest_zombie_between_positions(
        zombies, plant.row, plant.col, nearest_portal.col
    )

    if nearest_before_portal:
        return nearest_before_portal

    # 寻找其他传送门出口的僵尸
    return _find_nearest_zombie_at_portal_exits(zombies, portal_manager, nearest_portal)


def get_bullet_target_col_with_portal(plant, zombies, portal_manager):
    """获取子弹目标列位置，考虑传送门穿越"""
    target_zombie = find_nearest_zombie_with_portal(plant, zombies, portal_manager)

    if target_zombie:
        if _is_zombie_at_portal_exit(target_zombie, plant, portal_manager):
            plant_row_portals = _get_portals_in_row(portal_manager, plant.row)
            nearest_portal = _find_nearest_portal_to_right(plant, plant_row_portals)
            if nearest_portal:
                return float(nearest_portal.col)

        return target_zombie.col

    return 9.0


# ==================== 辅助函数 ====================

def _get_portals_in_row(portal_manager, row):
    """获取指定行的所有活跃传送门"""
    if not portal_manager or not hasattr(portal_manager, 'portals'):
        return []
    return [portal for portal in portal_manager.portals
            if portal.row == row and portal.is_active]


def _find_nearest_portal_to_right(plant, portals):
    """找到植物右侧最近的传送门"""
    nearest_portal = None
    min_distance = float('inf')

    for portal in portals:
        if portal.col > plant.col:
            distance = portal.col - plant.col
            if distance < min_distance:
                min_distance = distance
                nearest_portal = portal

    return nearest_portal


def _has_zombie_in_row_ahead_normal(plant, zombies):
    """普通的前方僵尸检测逻辑"""
    for zombie in zombies:
        if zombie.row == plant.row and zombie.col > plant.col:
            return True
    return False


def _find_nearest_zombie_normal(plant, zombies):
    """普通的最近僵尸寻找逻辑"""
    nearest_zombie = None
    min_distance = float('inf')

    for zombie in zombies:
        if zombie.row == plant.row and zombie.col > plant.col:
            distance = zombie.col - plant.col
            if distance < min_distance:
                min_distance = distance
                nearest_zombie = zombie

    return nearest_zombie


def _has_zombie_between_positions(zombies, row, start_col, end_col):
    """检查指定位置范围内是否有僵尸"""
    for zombie in zombies:
        if (zombie.row == row and start_col < zombie.col < end_col):
            return True
    return False


def _find_nearest_zombie_between_positions(zombies, row, start_col, end_col):
    """寻找指定位置范围内最近的僵尸"""
    nearest_zombie = None
    min_distance = float('inf')

    for zombie in zombies:
        if (zombie.row == row and start_col < zombie.col < end_col):
            distance = zombie.col - start_col
            if distance < min_distance:
                min_distance = distance
                nearest_zombie = zombie

    return nearest_zombie


def _has_zombie_at_portal_exits(zombies, portal_manager, source_portal):
    """检查其他传送门出口是否有僵尸"""
    if not portal_manager or not hasattr(portal_manager, 'portals'):
        return False

    exit_portals = [portal for portal in portal_manager.portals
                    if (portal.is_active and portal != source_portal)]

    for exit_portal in exit_portals:
        for zombie in zombies:
            if (zombie.row == exit_portal.row and zombie.col > exit_portal.col):
                return True

    return False


def _find_nearest_zombie_at_portal_exits(zombies, portal_manager, source_portal):
    """寻找其他传送门出口最近的僵尸"""
    if not portal_manager or not hasattr(portal_manager, 'portals'):
        return None

    exit_portals = [portal for portal in portal_manager.portals
                    if (portal.is_active and portal != source_portal)]

    nearest_zombie = None
    min_total_distance = float('inf')

    for exit_portal in exit_portals:
        for zombie in zombies:
            if (zombie.row == exit_portal.row and zombie.col > exit_portal.col):
                distance_from_exit = zombie.col - exit_portal.col
                if distance_from_exit < min_total_distance:
                    min_total_distance = distance_from_exit
                    nearest_zombie = zombie

    return nearest_zombie


def _is_zombie_at_portal_exit(zombie, plant, portal_manager):
    """检查僵尸是否位于传送门出口"""
    if not portal_manager:
        return False

    plant_row_portals = _get_portals_in_row(portal_manager, plant.row)

    if not plant_row_portals:
        return False

    nearest_portal = _find_nearest_portal_to_right(plant, plant_row_portals)

    if not nearest_portal:
        return False

    exit_portals = [portal for portal in portal_manager.portals
                    if (portal.is_active and portal != nearest_portal)]

    for exit_portal in exit_portals:
        if zombie.row == exit_portal.row:
            return True

    return False