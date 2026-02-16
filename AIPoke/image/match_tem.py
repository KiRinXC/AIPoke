import cv2
import numpy as np
from AIPoke.image.get_tem import get_tem

def match_static(frame, region, template, threshold=240,confidence=0.95):
    """
    【静态极速对比】
    适用场景：Region的大小和Template的大小完全一致（1:1）。
    原理：使用异或运算 (XOR) 计算差异像素，速度最快。
    """
    # 1. 获取二值化的 ROI
    # 假设 get_tem 返回的是 uint8 格式的二值图 (0 和 255)
    binary_roi = get_tem(frame, region,threshold)

    # 2. 核心算法：异或运算 (Bitwise XOR)
    # 原理：相同为0，不同为255 (或1)
    diff = cv2.bitwise_xor(binary_roi, template)

    # 3. 计算不匹配的像素点数量
    non_zero_count = cv2.countNonZero(diff)

    # 4. 计算相似度
    # 相似度 = 1 - (不一样的点 / 总点数)
    total_pixels = template.size # 高 x 宽
    match_rate = 1 - (non_zero_count / total_pixels)
    # print("match_rate:", match_rate)
    return match_rate >= confidence


def match_dynamic(frame, region, template, threshold=240,confidence=0.85):
    """
    【动态搜索对比】
    适用场景：Region 比 Template 大，需要在 Region 里找 Template。
    原理：标准模板匹配 (Convolution)。
    """
    binary_roi = get_tem(frame, region,threshold)

    # 核心算法：标准模板匹配
    res = cv2.matchTemplate(binary_roi, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    # print("max_val:", max_val)
    return max_val >= confidence


def verify_area(image_path, region, template, confidence=0.85):
    """
    【通用验证函数】验证 给定图片 的特定区域是否匹配模板。
    会自动截取区域、进行二值化，并根据尺寸自动选择最快的匹配算法。

    参数:
        img:        图片路径
        region:     区域 [x, y, w, h]
        template:   预加载的模板 (Gray/Binary, HxW)
        threshold:  二值化阈值 (默认 245，针对纯白文字)
        confidence: 匹配置信度 (默认 0.85)

    返回:
        bool: 是否匹配
    """
    frame = cv2.imread(image_path)
    binary_roi = get_tem(frame, region)
    cv2.imwrite("verify_tem.png", binary_roi)
    print(binary_roi.shape,template.shape)
    res = cv2.matchTemplate(binary_roi, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    return max_val >= confidence

def verify_match(curr_roi, old_roi, threshold=2.0):
    """
    验证 两个frame 是否匹配
    :param curr_roi:
    :param old_roi:
    :param threshold:
    :return:
    """
    # [关键] 转换为 int32 进行计算，防止 uint8 溢出
    # 计算 绝对差值 的 平均值
    # 逻辑：|当前 - 过去| -> 求和 -> 除以像素数
    diff_score = np.mean(np.abs(curr_roi.astype(int) - old_roi.astype(int)))

    # 如果差异很小 (score < threshold)，说明画面没变
    return diff_score < threshold


