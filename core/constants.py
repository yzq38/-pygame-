"""
游戏常量和配置文件
"""
import pygame

# 游戏基础尺寸
BASE_WIDTH = 900
BASE_HEIGHT = 700
SCREEN_WIDTH = BASE_WIDTH
SCREEN_HEIGHT = BASE_HEIGHT

# 网格设置
GRID_SIZE = 80
GRID_GAP = 12
GRID_WIDTH = 9
GRID_HEIGHT = 5

# 计算战场区域的偏移量，使其居中
total_battlefield_width = GRID_WIDTH * GRID_SIZE + (GRID_WIDTH - 1) * GRID_GAP
total_battlefield_height = GRID_HEIGHT * GRID_SIZE + (GRID_HEIGHT - 1) * GRID_GAP
BATTLEFIELD_TOP = 150
BATTLEFIELD_LEFT = (BASE_WIDTH - total_battlefield_width) // 2

# 卡片相关 - 阳光右侧
CARD_WIDTH = 80
CARD_HEIGHT = 100
CARD_Y = 20
CARD_START_X = 180

# 铲子相关
SHOVEL_WIDTH = 60
SHOVEL_HEIGHT = CARD_HEIGHT
SHOVEL_X = BASE_WIDTH - SHOVEL_WIDTH - 20  # 右上角，距离右边缘20像素
SHOVEL_Y = CARD_Y  # 和卡片同一高度
SHOVEL_COLOR = (139, 69, 19)
# 锤子位置和尺寸（在铲子左侧）
HAMMER_WIDTH = 80
HAMMER_HEIGHT = 80
HAMMER_X = SHOVEL_X - HAMMER_WIDTH - 1  # 铲子左侧，间隔10像素
HAMMER_Y = SHOVEL_Y
HAMMER_COLOR = (180, 90, 0)  # 棕色

# 锤子冷却时间（秒转换为帧，60FPS）
HAMMER_COOLDOWN_TIME = 20 * 60  # 20秒 = 1200帧

# 设置按钮相关
SETTINGS_BUTTON_WIDTH = 50
SETTINGS_BUTTON_HEIGHT = 50
SETTINGS_BUTTON_X = BASE_WIDTH - SETTINGS_BUTTON_WIDTH - 20
SETTINGS_BUTTON_Y = BASE_HEIGHT - SETTINGS_BUTTON_HEIGHT - 20

# 阳光相关设置
MAX_SUN = 1000  # 每关最大阳光数量

# 颜色定义
GREEN = (0, 255, 0)
ORANGE = (255, 204, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
BLACK = (0, 160, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ARMOR_COLOR = (184, 134, 11)
GRAY_DARK = (50, 50, 50)
LIGHT_BLUE = (100, 150, 255)
DARK_BLUE = (50, 100, 200)

# 游戏平衡设置
NORMAL_SPAWN_DELAY = 180
WAVE_INTERVAL = 360
MAX_NORMAL_ZOMBIES = 100

# 图鉴按钮相关常量
CODEX_BUTTON_SIZE = 80  # 图鉴按钮尺寸（正方形）
CODEX_BUTTON_X = 100  # 与商店按钮同一水平位置
CODEX_BUTTON_Y = BASE_HEIGHT // 2 - 50  # 在商店按钮上方


def get_constants():
    """获取常量字典，供Plant和Zombie类使用"""
    return {
        'BATTLEFIELD_LEFT': BATTLEFIELD_LEFT,
        'BATTLEFIELD_TOP': BATTLEFIELD_TOP,
        'GRID_SIZE': GRID_SIZE,
        'GRID_GAP': GRID_GAP,
        'GRID_WIDTH': GRID_WIDTH,
        'GRID_HEIGHT': GRID_HEIGHT,
        'GREEN': GREEN,
        'ORANGE': ORANGE,
        'GRAY': GRAY,
        'RED': RED,
        'BLUE': BLUE,
        'ARMOR_COLOR': ARMOR_COLOR,
        'WHITE': WHITE,
        'BITE_INTERVAL': 30,
        'MAX_SUN': MAX_SUN
    }


def add_sun_safely(current_sun, amount_to_add):
    """
    安全地增加阳光，确保不超过上限

    Args:
        current_sun: 当前阳光数量
        amount_to_add: 要增加的阳光数量

    Returns:
        int: 增加后的阳光数量（不超过上限）
    """
    return min(current_sun + amount_to_add, MAX_SUN)