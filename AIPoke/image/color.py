import numpy as np


def _check_pixel(frame, region, threshold, color_mode='white', check_mode='any'):
    """
    【核心通用函数】检测区域内的像素颜色条件。

    参数:
        color_mode: 'white' (检测高亮 > threshold) 或 'black' (检测暗色 < threshold)
        check_mode: 'any' (只要有一个像素满足) 或 'all' (所有像素都满足)
    """
    if frame is None:
        return False

    x, y, w, h = region
    # 1. 切片 (Zero-copy)
    roi = frame[y: y + h, x: x + w]

    # 2. 生成掩膜 (Mask) - 性能优化写法
    # axis=-1 表示在颜色通道(B,G,R)维度上操作
    if color_mode == 'white':
        # 如果 RGB 中最小的值都 > 阈值，说明三个通道都 > 阈值 (即白色)
        # 这比写 (B>t) & (G>t) & (R>t) 更快更简洁
        mask = np.min(roi, axis=-1) > threshold
    else:  # black
        # 如果 RGB 中最大的值都 < 阈值，说明三个通道都 < 阈值 (即黑色)
        mask = np.max(roi, axis=-1) < threshold

    # 3. 结果聚合
    if check_mode == 'any':
        return np.any(mask)
    else:  # all
        return np.all(mask)


# ========================================================
# 下面是保留的接口函数 (Wrapper)，直接调用上面的核心函数
# ========================================================

def has_white_pix(frame, region, threshold=240):
    """检测区域内是否存在白色像素"""
    return _check_pixel(frame, region, threshold, color_mode='white', check_mode='any')


def has_black_pix(frame, region, threshold=10):
    """检测区域内是否存在黑色像素"""
    return _check_pixel(frame, region, threshold, color_mode='black', check_mode='any')


def all_white_pix(frame, region, threshold=240):
    """检测区域内是否 全是 白色像素"""
    return _check_pixel(frame, region, threshold, color_mode='white', check_mode='all')


def all_black_pix(frame, region, threshold=5):
    """检测区域内是否 全是 黑色像素"""
    return _check_pixel(frame, region, threshold, color_mode='black', check_mode='all')