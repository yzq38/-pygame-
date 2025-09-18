"""
音频管理模块 - 添加图鉴音乐支持
重构版本 - 路径更新到rsc_mng文件夹
"""
import pygame
import random
import os


class BackgroundMusicManager:
    def __init__(self):
        self.is_paused_for_sound = False
        self.sound_end_time = 0
        self.was_playing = False
        self.current_game_state = None
        self.current_music_file = None

        # 新增：音乐播放时间追踪
        self.music_start_time = 0
        self.music_pause_time = 0
        self.total_paused_time = 0
        self.current_volume = 0.5
        self.is_music_playing = False

        # 定义不同游戏状态对应的音乐文件
        self.music_files = {
            "main_menu": "Laura Shigihara - Faster.ogg",
            "level_select": "Laura Shigihara - Look up at the Sky.ogg",
            "shop": "Laura Shigihara - 芝生にゾンビが.ogg",
            "codex": "Laura Shigihara - 芝生にゾンビが.ogg",  # 图鉴使用和商店一样的音乐
            "playing": [
                "Laura Shigihara - Kitanai Sekai.ogg",
                "Laura Shigihara - Loonboon.ogg",
                "Laura Shigihara - Ultimate Battle.ogg",
                "Laura Shigihara - Uraniwa ni Zombies ga!.ogg",
            ]
        }

    def get_current_play_time(self):
        """获取当前音乐的播放时间（秒）"""
        if not self.is_music_playing:
            return 0

        current_time = pygame.time.get_ticks()
        if self.music_start_time == 0:
            return 0

        # 计算实际播放时间（排除暂停时间）
        elapsed_time = (current_time - self.music_start_time - self.total_paused_time) / 1000.0
        return max(0, elapsed_time)

    def set_volume(self, volume):
        """设置音乐音量"""
        self.current_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.current_volume)

    def pause_for_sound(self, sound_duration):
        """为播放音效暂停背景音乐"""
        if pygame.mixer.music.get_busy():
            self.was_playing = True
            pygame.mixer.music.pause()
            self.is_paused_for_sound = True
            self.music_pause_time = pygame.time.get_ticks()
            # 设置音效结束时间（当前时间 + 音效长度 + 200ms缓冲）
            self.sound_end_time = pygame.time.get_ticks() + int(sound_duration * 1000) + 200
        else:
            self.was_playing = False

    def update(self):
        """更新背景音乐状态，检查是否需要恢复播放"""
        if self.is_paused_for_sound:
            current_time = pygame.time.get_ticks()
            if current_time >= self.sound_end_time:
                self.resume_after_sound()

    def resume_after_sound(self):
        """音效播放完毕后恢复背景音乐"""
        if self.is_paused_for_sound and self.was_playing:
            pygame.mixer.music.unpause()

            # 累计暂停时间
            if self.music_pause_time > 0:
                pause_duration = pygame.time.get_ticks() - self.music_pause_time
                self.total_paused_time += pause_duration
                self.music_pause_time = 0

            self.is_paused_for_sound = False
            self.sound_end_time = 0

    def change_music_for_state(self, new_game_state, start_position=0):
        """根据游戏状态切换背景音乐"""

        # 定义使用相同音乐的状态组
        state_music_groups = {
            "main_menu": "main_menu",
            "level_select": "level_select",
            "level_settings": "level_select",  # 关卡设置使用与选关页面相同的音乐
            "shop": "shop",
            "codex": "codex",  # 图鉴主页
            "codex_detail": "codex",  # 详细图鉴页面 - 关键修改：使用相同的音乐组
            "playing": "playing"
        }

        # 获取当前状态和新状态对应的音乐状态
        current_music_state = state_music_groups.get(self.current_game_state, self.current_game_state)
        new_music_state = state_music_groups.get(new_game_state, new_game_state)

        # 如果音乐状态没有改变，不需要切换音乐
        if new_music_state == current_music_state and start_position == 0:
            return

        # 停止当前音乐
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        # 更新当前游戏状态（这里仍然更新实际的游戏状态）
        self.current_game_state = new_game_state

        # 根据新的音乐状态播放对应音乐
        if new_music_state in self.music_files:
            music_to_play = self.music_files[new_music_state]

            # 对于游戏内音乐，随机选择一首
            if new_music_state == "playing":
                music_to_play = random.choice(music_to_play)

            # 加载并播放新音乐
            if self._load_and_play_music(music_to_play, start_position):
                self.current_music_file = music_to_play
                self.music_start_time = pygame.time.get_ticks() - (start_position * 1000)
                self.total_paused_time = 0
                self.is_music_playing = True
                # 应用当前音量设置
                pygame.mixer.music.set_volume(self.current_volume)
            else:
                print(f"无法加载音乐文件: {music_to_play}")

    def _load_and_play_music(self, music_file, start_position=0):
        """加载并播放指定的音乐文件"""
        try:
            # 重构：更新音乐文件路径到rsc_mng/sounds文件夹
            music_path = os.path.join("rsc_mng", "sounds", music_file)
            pygame.mixer.music.load(music_path)

            # 注意：pygame.mixer.music不支持从指定位置开始播放
            # 这里我们先正常播放，然后通过时间追踪来模拟位置
            pygame.mixer.music.play(-1)  # -1表示无限循环

            # 如果需要从指定位置开始，我们可以通过调整开始时间来模拟
            if start_position > 0:
                # 调整开始时间，使get_current_play_time()返回正确的播放时间
                self.music_start_time = pygame.time.get_ticks() - (start_position * 1000)

            pygame.mixer.music.set_volume(self.current_volume)
            return True
        except Exception as e:
            print(f"无法加载音乐 {music_file}: {e}")
            return False

    def get_music_state(self):
        """获取当前音乐状态，用于保存"""
        return {
            "current_music_file": self.current_music_file,
            "is_playing": self.is_music_playing and pygame.mixer.music.get_busy(),
            "play_time": self.get_current_play_time(),
            "volume": self.current_volume
        }

    def restore_music_state(self, music_state):
        """从保存的状态恢复音乐播放"""
        if not music_state:
            return

        music_file = music_state.get("current_music_file")
        was_playing = music_state.get("is_playing", False)
        play_time = music_state.get("play_time", 0)
        volume = music_state.get("volume", 0.5)

        # 恢复音量设置
        self.set_volume(volume)

        if music_file and was_playing:
            try:
                # 恢复音乐播放
                if self._load_and_play_music(music_file, play_time):
                    self.current_music_file = music_file
                    self.is_music_playing = True

            except Exception as e:
                print(f"")

    def ensure_music_playing(self, game_state):
        """确保当前游戏状态的音乐正在播放（用于处理音乐自然结束的情况）"""
        # 如果音乐没有在播放且没有被音效暂停，重新开始播放
        if not pygame.mixer.music.get_busy() and not self.is_paused_for_sound:
            self.change_music_for_state(game_state)


def load_sound(file_name):
    """加载音效"""
    try:
        # 重构：更新音效文件路径到rsc_mng/sounds文件夹
        sound_path = os.path.join("rsc_mng", "sounds", file_name)
        return pygame.mixer.Sound(sound_path)
    except Exception as e:
        print(f"无法加载音效 {file_name}: {e}")
        return None


def play_sound_with_music_pause(sound, duration=None, music_manager=None):
    """播放音效并暂停背景音乐，音效播放完毕后恢复背景音乐"""
    if sound and music_manager:
        if duration is None:
            # 尝试获取音效长度
            try:
                duration = sound.get_length()
            except:
                duration = 2.0  # 默认2秒

        # 暂停背景音乐
        music_manager.pause_for_sound(duration)
        # 播放音效
        sound.play()
    elif sound:
        # 如果没有音乐管理器，直接播放音效
        sound.play()


def initialize_sounds():
    """初始化所有音效"""
    try:
        sounds = {
            "zombie_hit": load_sound("普僵受击.mp3"),
            "plant_place": load_sound("种植.mp3"),
            "bite": load_sound("啃咬.mp3"),
            "wave_warning": load_sound("波次预警.mp3"),
            "armor_hit": load_sound("铁器受击.mp3"),
            "game_over": load_sound("失败音效.ogg"),
            "victory": load_sound("胜利.mp3"),
            "watermelon_hit": load_sound("watermelon_hitting.mp3"),
            "cherry_explosion": load_sound("樱桃爆炸.mp3"),
            "dandelion_shoot": load_sound("蒲公英发射.mp3"),
            "lightning_flower": load_sound("lightning.mp3"),
            "冻结": load_sound("冻结.mp3"),
        }

        # 设置音效音量
        for sound in sounds.values():
            if sound:
                sound.set_volume(0.7)

        return sounds
    except Exception as e:
        print(f"加载音效时出错: {e}")
        return {}


def set_sounds_volume(sounds, volume):
    """设置所有音效的音量"""
    for sound in sounds.values():
        if sound:
            sound.set_volume(volume)