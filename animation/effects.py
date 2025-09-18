"""
动画效果函数库 - 提供各种缓动函数
"""
import math


class AnimationEffects:
    """动画效果类 - 提供各种缓动函数"""

    @staticmethod
    def ease_in_cubic(t):
        """三次方缓入函数"""
        return t * t * t

    @staticmethod
    def ease_out_cubic(t):
        """三次方缓出函数"""
        return 1 - pow(1 - t, 3)

    @staticmethod
    def ease_in_out_cubic(t):
        """三次方缓入缓出函数"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2

    @staticmethod
    def ease_in_quart(t):
        """四次方缓入函数，开始慢，加速明显"""
        return t * t * t * t

    @staticmethod
    def ease_out_quart(t):
        """四次方缓出函数，减速更明显"""
        return 1 - pow(1 - t, 4)

    @staticmethod
    def ease_out_bounce(t):
        """弹跳缓出函数"""
        n1 = 7.5625
        d1 = 2.75

        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            return n1 * (t - 1.5 / d1) * t + 0.75
        elif t < 2.5 / d1:
            return n1 * (t - 2.25 / d1) * t + 0.9375
        else:
            return n1 * (t - 2.625 / d1) * t + 0.984375