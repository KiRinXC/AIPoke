import numpy as np
def has_white_pix(frame, region, threshold=240):
    """
    检测指定区域内是否存在白色（或高亮）像素。

    参数:
        frame: 原始的大图 (numpy array, BGR格式)
        region: 检测区域元组 (x, y, w, h)
        threshold: 白色判定阈值 (0-255).
                   255 表示必须是纯白.
                   200 表示只要 RGB 三个通道都大于 200 就算白色 (推荐).
    返回:
        bool: 如果存在白色像素返回 True, 否则 False
    """
    if frame is None:
        return False

    x, y, w, h = region

    # 1. 切片截取区域 (Zero-copy, 极快)
    # 注意 NumPy 顺序: [y : y+h, x : x+w]
    roi = frame[y: y + h, x: x + w]

    # 2. 核心检测逻辑 (利用 NumPy 的广播机制)
    # 逻辑：蓝色通道 > 阈值 AND 绿色通道 > 阈值 AND 红色通道 > 阈值
    # frame[:, :, 0] 是 B 通道
    # frame[:, :, 1] 是 G 通道
    # frame[:, :, 2] 是 R 通道

    # 这行代码会生成一个布尔矩阵 (True/False)，计算速度是纳秒级
    mask = (roi[:, :, 0] > threshold) & \
           (roi[:, :, 1] > threshold) & \
           (roi[:, :, 2] > threshold)

    # 3. 只要有一个像素满足条件，就返回 True
    return np.any(mask)