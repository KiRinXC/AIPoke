import numpy as np


def get_tem(frame, region, threshold=240):
    """
    使用 NumPy 进行极速二值化，跳过转灰度图步骤。
    针对纯白文字优化。
    """
    # 1. 切片 (Zero-copy)
    x, y, w, h = region
    roi = frame[y:y + h, x:x + w]

    # 2. NumPy 核心操作
    # 逻辑：判断每个像素的 B, G, R 是否都大于阈值
    # axis=-1 表示在最后一个维度（颜色通道）上进行操作
    # mask 是一个布尔矩阵 (True/False)
    mask = np.all(roi > threshold, axis=-1)

    # 3. 转换格式 (关键步骤)
    # cv2.matchTemplate 需要 uint8 格式 (0 或 255)，不能直接吃布尔值
    # astype 转换极其快速
    binary_roi = mask.astype(np.uint8) * 255

    return binary_roi

