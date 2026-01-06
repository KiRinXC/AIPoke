from AIPoke.image.color import has_white_pix,all_black_pix
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
            return {k: False for k in self.rio["obs"]}

        # 2. 遍历四个区域进行对比
        for name, (x, y, w, h) in self.rio["obs"].items():
            # --- 核心 NumPy 对比逻辑 ---

            # 切片获取当前帧区域和上一帧区域
            curr_roi = frame[y:y + h, x:x + w]
            old_roi = self.old_frame[y:y + h, x:x + w]
            result[name] = verify_match(curr_roi, old_roi)

        #更新旧帧，供下一次对比使用
        self.old_frame = frame.copy()

        return result



