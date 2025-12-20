import numpy as np
from image.color import has_white_pix
from image.match_tem import match_static,match_dynamic
from utili.tem_manager import load_all_templates
from utili.path_manager import TEM_DIR


rio_dict={
    "nickname":[570,409,20,10],
    "escape":[473, 640, 27, 12],
    "obs" :{
        "left":  (520, 465, 10, 10),
        "right": (630, 465, 10, 10),
        "up":    (575, 410, 10, 10),
        "down":  (575, 520, 10, 10)
    }
}

tem_dict = load_all_templates(template_dir=TEM_DIR)

class Detect:
    def __init__(self):
        self.old_frame = None
        self.static_threshold = 2.0 # 撞墙

    def det_nickname(self,frame):
        return has_white_pix(frame,rio_dict["nickname"])

    def det_escape(self,frame):
        return match_static(frame,rio_dict["escape"],tem_dict["escape"])

    def det_obs(self, frame):
        """
        检测障碍物
        :param frame: 当前帧 (NumPy数组)
        :return: 字典, 例如 {'obs_left': True, 'obs_right': False}
                 True 表示该方向画面静止（可能撞墙），False 表示画面在变（通畅）
        """
        result = {}

        # 1. 如果没有上一帧，先存下来，无法判断
        if self.old_frame is None:
            self.old_frame = frame.copy()  # 必须用 copy!
            # 默认返回全 False (未撞墙) 或者 None
            return {k: False for k in rio_dict["obs"]}

        # 2. 遍历四个区域进行对比
        for name, (x, y, w, h) in rio_dict["obs"].items():
            # --- 核心 NumPy 对比逻辑 ---

            # 切片获取当前帧区域和上一帧区域
            curr_roi = frame[y:y + h, x:x + w]
            old_roi = self.old_frame[y:y + h, x:x + w]

            # [关键] 转换为 int32 进行计算，防止 uint8 溢出
            # 计算 绝对差值 的 平均值
            # 逻辑：|当前 - 过去| -> 求和 -> 除以像素数
            diff_score = np.mean(np.abs(curr_roi.astype(int) - old_roi.astype(int)))

            # 3. 判断结果
            # 如果差异很小 (score < threshold)，说明画面没变 -> 撞墙了
            result[name] = diff_score < self.static_threshold

        # 4. [重要] 更新旧帧，供下一次对比使用
        self.old_frame = frame.copy()

        return result



