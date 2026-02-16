from collections import deque
import cv2
import numpy as np

from AIPoke.image.color import has_white_pix,all_black_pix,all_white_pix
from AIPoke.image.match_tem import match_static, verify_match, match_dynamic
from AIPoke.utili.tem_manager import load_all_templates
from AIPoke.utili.path_manager import TEM_DIR
from AIPoke.utili.data_manager import RIO_DET



tem_dict = load_all_templates(template_dir=TEM_DIR)

class Detect:
    def __init__(self):
        self.old_frame = None
        self.static_threshold = 2.0 # 撞墙
        self.rio = RIO_DET
        self.obs_queue_len = 5
        self.obs_queues = {
            k: deque([False] * self.obs_queue_len, maxlen=self.obs_queue_len) for k in self.rio["obs"]
        }
        self.old_gray_rois = {}  # 存储上一次的灰度图

    def det_nickname(self,frame):
        rio_1 = has_white_pix(frame, self.rio["nickname"][0]) # 对应丰源关都
        rio_2= has_white_pix(frame, self.rio["nickname"][1])  # 对应合众
        return rio_1 or rio_2

    def det_escape(self,frame):
        return match_static(frame,self.rio["escape"],tem_dict["escape"])

    def det_battle_background(self,frame):
        return all_black_pix(frame,self.rio["battle_background"])

    def det_pop_win(self,frame):
        """出现弹窗的话，应该是lab1 False   lab2 True"""
        lab1 = all_black_pix(frame,self.rio["pop_win"],threshold=5)  # 画面全黑
        lab2 =  all_black_pix(frame,self.rio["pop_win"],threshold=20) # 出现弹窗
        return lab1 ^ lab2

    def det_hp_bar(self,frame):
        """检测血量条是否出现"""
        return match_dynamic(frame,self.rio["hp_bar"],tem_dict["hp_bar"])

    def det_poke_ditto(self,frame):
        """检测是否是百变怪"""
        return match_dynamic(frame,self.rio["poke_info"],tem_dict["poke_ditto"])

    def det_zzz(self,frame):
        """检测是否睡着"""
        return match_dynamic(frame,self.rio["zzz"],tem_dict["zzz"])

    def det_pokedex(self,frame):
        """检测是否出现捕捉成功后的图鉴"""
        return match_static(frame,self.rio["pokedex"],tem_dict["pokedex"])

    def det_underpass_obs(self,frame):
        left_obs = match_static(frame,self.rio["underpass_left_obs"],tem_dict["underpass_left_obs"],threshold=50)
        right_obs = match_static(frame, self.rio["underpass_right_obs"], tem_dict["underpass_right_obs"],threshold=50)
        return left_obs,right_obs

    def det_chat_win(self,frame):
        """检测是否出现聊天提示框"""
        return all_white_pix(frame,self.rio["chat_win"])

    def det_hatch_egg_button(self,frame):
        """检测是否出现孵蛋按钮"""
        return match_dynamic(frame,self.rio["hatch_egg_button"],tem_dict["hatch_egg_button"])

    def det_computer_box(self,frame):
        """检测是否出现电脑箱子"""
        return match_static(frame,self.rio["computer_box"],tem_dict["computer_box"])

    def det_select_parent(self,frame):
        """检测是否出现选择父母界面"""
        return match_dynamic(frame,self.rio["select_parent"],tem_dict["select_parent"],confidence=0.30)


    def det_obs(self, frame, directions):
        """
        检测移动方向的障碍物
        :param frame: 当前帧 (NumPy数组)
        :param directions: 移动方向
        :return: True  -> 成对方向异或为 1（一个静止一个运动）
                 False -> 成对方向状态相同，或尚未集齐两个方向
        """
        # 首帧：只能缓存，无法判断
        if self.old_frame is None:
            self.old_frame = frame.copy()
            return False,False

        results = []  # 存储本轮各个方向的最终判定结果
        for name in directions:
            x, y, w, h = self.rio["obs"][name]
            curr_roi = frame[y:y + h, x:x + w]
            old_roi = self.old_frame[y:y + h, x:x + w]
            is_static_now = verify_match(curr_roi, old_roi)

            self.obs_queues[name].append(is_static_now)
            results.append(all(self.obs_queues[name]))
        # 更新旧帧
        self.old_frame = frame.copy()
        # 异或：只有一静一动才认为“卡住”
        return results[0],results[1]

    def det_obs_optical_flow(self, frame, directions):
        """
        基于光流法的障碍物检测
        :return: True (卡住了/静止), False (在移动)
        """
        status = []

        # 将整帧转为灰度，减少计算量
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for name in directions:
            x, y, w, h = self.rio["obs"][name]
            curr_gray_roi = gray_frame[y:y + h, x:x + w]

            # 第一次运行，先存图，无法判断
            if name not in self.old_gray_rois:
                self.old_gray_rois[name] = curr_gray_roi
                status.append(False)
                continue

            prev_gray_roi = self.old_gray_rois[name]

            # --- 核心：计算稠密光流 ---
            # 参数解释：pyr_scale=0.5, levels=3, winsize=15, iterations=3, poly_n=5, poly_sigma=1.2, flags=0
            # 这些参数平衡了速度和精度，适合实时检测
            flow = cv2.calcOpticalFlowFarneback(prev_gray_roi, curr_gray_roi, None,
                                                0.5, 3, 15, 3, 5, 1.2, 0)

            # flow 是一个 (h, w, 2) 的数组，包含 x 和 y 方向的移动量
            # 计算运动的模长 (magnitude)
            mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])

            # 计算区域内的平均移动量
            mean_movement = np.mean(mag)

            # 调试：打印平均移动量，你可以根据这个值调整阈值
            # print(f"Direction {name}: Movement {mean_movement:.2f}")

            # 如果平均移动量小于阈值（例如 1.0 像素），认为卡住了
            # 这里解决了“纹理重复”问题，因为只要有像素位移，这个值就会大于0
            is_stuck = mean_movement < 1.0
            status.append(is_stuck)

            # 更新旧帧
            self.old_gray_rois[name] = curr_gray_roi

        # 结合之前的队列机制使用效果更佳
        return status





# #
# detect = Detect()
# from AIPoke.image.Camera import Camera
# import time
# camera = Camera()
# while True:
#     frame = camera.grab()
#     flag = detect.det_select_parent(frame)
#     print(flag)
#     time.sleep(0.1)



