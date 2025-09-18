"""
资源加载模块 - 处理图片和其他资源的加载
重构版本 - 路径更新到rsc_mng文件夹
"""
import os
import sys

import pygame


from core.constants import *


def load_image(name, size=None):
    """加载图片资源"""
    try:
        # 重构：更新图片文件路径到rsc_mng/images文件夹
        image = pygame.image.load(f"rsc_mng/images/{name}.png").convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except:
        print(f"无法加载图片: rsc_mng/images/{name}.png")
        # 创建一个占位符表面
        surf = pygame.Surface(size if size else (GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        surf.fill((255, 0, 255, 128))  # 半透明洋红色作为占位符
        return surf


def load_all_images():
    """加载所有游戏图片资源"""
    try:
        images = {
            # 植物图片
            'pea_shooter_img': load_image("peashooter", (GRID_SIZE, GRID_SIZE)),
            'sunflower_img': load_image("sunflower", (GRID_SIZE, GRID_SIZE)),
            'watermelon_img': load_image("watermelon", (GRID_SIZE, GRID_SIZE)),
            'cattail_img': load_image("cattail", (GRID_SIZE, GRID_SIZE)),
            'wall_nut_img': load_image("wall_nut", (GRID_SIZE, GRID_SIZE)),
            'cherry_bomb_img': load_image("cherry_bomb", (GRID_SIZE, GRID_SIZE)),
            'cucumber_img': load_image("cucumber", (GRID_SIZE, GRID_SIZE)),
            'dandelion_img': load_image("dandelion", (GRID_SIZE, GRID_SIZE)),
            'lightning_flower_img': load_image("lightning_flower", (GRID_SIZE, GRID_SIZE)),
            'ice_cactus_img': load_image("ice_cactus", (GRID_SIZE, GRID_SIZE)),

            # 僵尸图片
            'zombie_img': load_image("zombie", (GRID_SIZE, GRID_SIZE)),
            'zombie_armor_img': load_image("zombie_armor", (GRID_SIZE, GRID_SIZE)),
            'giant_zombie_img': load_image("giant_zombie", (int(GRID_SIZE * 1.5), int(GRID_SIZE * 1.5))),

            # 子弹图片
            'pea_img': load_image("pea", (20, 20)),
            'watermelon_bullet_img': load_image("watermelon_bullet", (20, 20)),
            'spike_img': load_image("spike", (24, 18)),
            'dandelion_seed_img': load_image("dandelion_seed", (24, 24)),
            'ice_bullet_img': load_image("ice_bullet", (24, 24)),

            # 防具图片
            'armor_img': load_image("armor", (GRID_SIZE - 10, GRID_SIZE - 10)),

            # 背景和UI元素
            'grid_bg_img': load_image("grid_bg", (GRID_SIZE, GRID_SIZE)),
            'card_bg_img': load_image("card_bg", (CARD_WIDTH, CARD_HEIGHT)),
            'shovel_img': load_image("shovel", (SHOVEL_WIDTH, SHOVEL_HEIGHT)),
            'hammer_img': load_image("hammer", (SHOVEL_WIDTH, SHOVEL_HEIGHT)),
            'settings_img': load_image("settings", (SETTINGS_BUTTON_WIDTH, SETTINGS_BUTTON_HEIGHT)),

            # 主菜单背景
            'menu_bg_img': load_image("menu_bg", (BASE_WIDTH, BASE_HEIGHT)),
            'trophy_img': load_image("trophy", (60, 60)),
            #小推车
            'cart_img':load_image("cart",(35,35))
        }
        return images
    except Exception as e:
        print(f"加载图片时出错: {e}")
        # 返回空字典，游戏将使用颜色块作为占位符
        return {}


def get_images():
    """获取图片字典，供Plant、Zombie和Bullet类使用"""
    images = load_all_images()
    return {
        'pea_shooter_img': images.get('pea_shooter_img'),
        'sunflower_img': images.get('sunflower_img'),
        'watermelon_img': images.get('watermelon_img'),
        'cattail_img': images.get('cattail_img'),
        'zombie_img': images.get('zombie_img'),
        'armor_img': images.get('armor_img'),
        'pea_img': images.get('pea_img'),
        'watermelon_bullet_img': images.get('watermelon_bullet_img'),
        'spike_img': images.get('spike_img')  ,
        'wall_nut_img': images.get('wall_nut_img'),
        'cherry_bomb':images.get('cherry_bomb_img'),
        'cucumber': images.get('cucumber_img'),
        'dandelion': images.get('dandelion_img'),
        'dandelion_seed': images.get('dandelion_seed_img'),
        'hammer': images.get('hammer_img'),
        'lightning_flower': images.get('lightning_flower_img'),
        'ice_cactus': images.get('ice_cactus_img'),
        'ice_bullet': images.get('ice_bullet_img'),
    }


def preload_scaled_images():
    """预先加载所有需要缩放的图片，避免运行时缩放"""
    scaled_images = {}
    images = load_all_images()

    # 预缓存植物卡片图片（60x60）
    if images.get('pea_shooter_img'):
        scaled_images['pea_shooter_60'] = pygame.transform.scale(images['pea_shooter_img'], (60, 60))
    if images.get('sunflower_img'):
        scaled_images['sunflower_60'] = pygame.transform.scale(images['sunflower_img'], (60, 60))
    if images.get('watermelon_img'):
        scaled_images['watermelon_60'] = pygame.transform.scale(images['watermelon_img'], (60, 60))
    if images.get('cattail_img'):
        scaled_images['cattail_60'] = pygame.transform.scale(images['cattail_img'], (60, 60))
    if images.get('wall_nut_img'):
        scaled_images['wall_nut_60'] = pygame.transform.scale(images['wall_nut_img'], (60, 60))
    if images.get('cherry_bomb_img'):
        scaled_images['cherry_bomb_60'] = pygame.transform.scale(images['cherry_bomb_img'], (60, 60))
    if images.get('cucumber_img'):
        scaled_images['cucumber_60'] = pygame.transform.scale(images['cucumber_img'], (60, 60))
    if images.get('dandelion_img'):
        scaled_images['dandelion_60'] = pygame.transform.scale(images['dandelion_img'], (60, 60))
    if images.get('lightning_flower_img'):
        scaled_images['lightning_flower_60'] = pygame.transform.scale(images['lightning_flower_img'], (60, 60))
    if images.get('ice_cactus_img'):
        scaled_images['ice_cactus_60'] = pygame.transform.scale(images['ice_cactus_img'], (60, 60))


    # 添加原始大小的图像（用于图鉴的 large_icon_key）
    if images.get('pea_shooter_img'):
        scaled_images['pea_shooter_img'] = images['pea_shooter_img']
    if images.get('sunflower_img'):
        scaled_images['sunflower_img'] = images['sunflower_img']
    if images.get('watermelon_img'):
        scaled_images['watermelon_img'] = images['watermelon_img']
    if images.get('cattail_img'):
        scaled_images['cattail_img'] = images['cattail_img']
    if images.get('wall_nut_img'):
        scaled_images['wall_nut_img'] = images['wall_nut_img']
    if images.get('cherry_bomb_img'):
        scaled_images['cherry_bomb_img'] = images['cherry_bomb_img']
    if images.get('cucumber_img'):
        scaled_images['cucumber_img'] = images['cucumber_img']
    if images.get('dandelion_img'):
        scaled_images['dandelion_img'] = images['dandelion_img']
    if images.get('lightning_flower_img'):
        scaled_images['lightning_flower_img'] = images['lightning_flower_img']
    if images.get('ice_cactus_img'):
        scaled_images['ice_cactus_img'] = images['ice_cactus_img']

    # 添加僵尸图像（用于僵尸图鉴）
    if images.get('zombie_img'):
        scaled_images['zombie_img'] = images['zombie_img']
        scaled_images['zombie_60'] = pygame.transform.scale(images['zombie_img'], (60, 60))
    if images.get('zombie_armor_img'):
        scaled_images['zombie_armor_img'] = images['zombie_armor_img']
        scaled_images['cone_zombie_60'] = pygame.transform.scale(images['zombie_armor_img'], (60, 60))
        scaled_images['cone_zombie_img'] = images['zombie_armor_img']
    if images.get('giant_zombie_img'):
        scaled_images['giant_zombie_img'] = images['giant_zombie_img']
        scaled_images['bucket_zombie_60'] = pygame.transform.scale(images['giant_zombie_img'], (60, 60))
        scaled_images['bucket_zombie_img'] = images['giant_zombie_img']
        scaled_images['fast_zombie_60'] = pygame.transform.scale(images['giant_zombie_img'], (60, 60))
        scaled_images['fast_zombie_img'] = images['giant_zombie_img']
        scaled_images['giant_zombie_60'] = pygame.transform.scale(images['giant_zombie_img'], (60, 60))
        scaled_images['armored_zombie_60'] = pygame.transform.scale(images['giant_zombie_img'], (60, 60))
        scaled_images['armored_zombie_img'] = images['giant_zombie_img']



    # 预缓存设置按钮图片
    if images.get('settings_img'):
        scaled_images['settings_50'] = pygame.transform.scale(images['settings_img'], (50, 50))

    # 预缓存西瓜子弹图片
    if images.get('watermelon_bullet_img'):
        scaled_images['watermelon_bullet_40'] = pygame.transform.scale(images['watermelon_bullet_img'], (40, 40))

    # 预缓存尖刺子弹图片
    if images.get('spike_img'):
        scaled_images['spike_24'] = pygame.transform.scale(images['spike_img'], (24, 24))
    if images.get('ice_bullet_img'):
        scaled_images['ice_bullet_24'] = pygame.transform.scale(images['ice_bullet_img'], (24, 24))
    if images.get('dandelion_seed_img'):
        scaled_images['dandelion_seed_24'] = pygame.transform.scale(images['dandelion_seed_img'], (24, 24))
    if images.get('cart_img'):
        scaled_images['cart_img'] = images['cart_img']  # 保持原始大小35x35
        scaled_images['cart_30'] = pygame.transform.scale(images['cart_img'], (35, 35))
    if images.get('hammer_img'):
        scaled_images['hammer_img'] = images['hammer_img']  # 添加原始大小的锤子图片
        scaled_images['hammer_80'] = pygame.transform.scale(images['hammer_img'], (80, 80))

    if images.get('card_bg_img'):
        scaled_images['card_bg_img'] = images['card_bg_img']  # 保持原始大小
        scaled_images['card_bg_50'] = pygame.transform.scale(images['card_bg_img'], (50, 50))  # 商店图标大小

    # 预缓存灰化版本的图片（用于冷却状态）
    original_keys = list(scaled_images.keys())
    for key in original_keys:
        img = scaled_images[key]
        if not key.endswith('_gray'):
            gray_surface = img.copy()
            gray_surface.fill((128, 128, 128), special_flags=pygame.BLEND_MULT)
            scaled_images[key + '_gray'] = gray_surface

    return scaled_images


def initialize_fonts():
    """改进的字体初始化函数"""
    chinese_fonts = [
        "Microsoft YaHei",
        "微软雅黑",
        "SimHei",
        "黑体",
        "Arial Unicode MS",
        "Noto Sans CJK SC",
        "DejaVu Sans",
    ]

    for font_name in chinese_fonts:
        try:
            test_font = pygame.font.SysFont(font_name, 24)
            test_surface = test_font.render("测试", True, (255, 255, 255))

            if test_surface.get_width() > 10:  # 渲染成功
                font_tiny = pygame.font.SysFont(font_name, 18)
                font_small = pygame.font.SysFont(font_name, 24)
                font_medium = pygame.font.SysFont(font_name, 32)
                font_large = pygame.font.SysFont(font_name, 48)
                print(f"成功加载中文字体: {font_name}")
                return font_small, font_medium, font_large, font_tiny
        except:
            continue

    # 字体加载失败的回退
    print("中文字体加载失败，使用默认字体")
    font_tiny = pygame.font.Font(None, 18)
    font_small = pygame.font.Font(None, 24)
    font_medium = pygame.font.Font(None, 32)
    font_large = pygame.font.Font(None, 48)
    return font_small, font_medium, font_large, font_tiny