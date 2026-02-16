import time
import pydirectinput

from AIPoke.actor.Point import Point
from AIPoke.actor.Random import Random
from AIPoke.image.Camera import Camera
from AIPoke.utili.data_manager import RIO_MOUSE
# ================= 全局配置 =================
pydirectinput.PAUSE = 0.0
pydirectinput.FAILSAFE = False

class Mouse:
    def __init__(self):
        self.rand = Random()
        self.rio = RIO_MOUSE
        self.min = self.rio["min"]  #
        self.max = self.rio["max"]
        self.shake_drift_prob = self.rio["shake_drift_prob"]
        self.random_drift_prob = self.rio["random_drift_prob"]
        self.point = Point()


    def click(self,rio,button='left'):
        x, y = self.rand.gen_loc(rio)
        self.point.move_to(x,y)
        # 鼠标按下
        pydirectinput.mouseDown(x=x, y=y, button=button, _pause=False)

        # 随机按下时长
        time.sleep(self.rand.gauss(self.min,self.max))

        # 鼠标抬起
        pydirectinput.mouseUp(button=button, _pause=False)
        # 鼠标发生偏移
        self.point.shake_drift(prob=self.shake_drift_prob)
        time.sleep(self.rand.gauss(0,4.0,0.5))
        self.point.random_drift(prob=self.random_drift_prob)

class MOptions(Mouse):
    def __init__(self):
        super().__init__()
        self.battle = self.rio["battle"]
        self.bag = self.rio["bag"]
        self.pokemon = self.rio["pokemon"]
        self.escape = self.rio["escape"]

    def battle_click(self):
        self.click(self.battle)

    def bag_click(self):
        self.click(self.bag)

    def pokemon_click(self):
        self.click(self.pokemon)

    def escape_click(self):
        self.click(self.escape)



class MBar(Mouse):
    def __init__(self):
        super().__init__()
        self.perfume = self.rio['perfume']
        self.spray = self.rio['spray']
        self.sweet_scent = self.rio['sweet_scent']
        self.fish_rod = self.rio['fish_rod']

        self.pokeball = self.rio['pokeball']

    def perfume_click(self):
        self.click(self.perfume)

    def spray_click(self):
        self.click(self.spray)

    def sweet_scent_click(self):
        self.click(self.sweet_scent)

    def fish_rod_click(self):
        self.click(self.fish_rod)

    def pokeball_click(self):
        self.click(self.pokeball)

class MInfoWin(Mouse):
    def __init__(self):
        super().__init__()
        self.iv = self.rio["iv"]
        self.pokedex_cancel = self.rio["pokedex_cancel"]
        self.chat_win = self.rio["chat_win"]

    def iv_click(self):
        self.click(self.iv)

    def pokedex_cancel_click(self):
        self.click(self.pokedex_cancel)

    def chat_win_click(self):
        self.click(self.chat_win)


class MBox(Mouse):
    def __init__(self):
        super().__init__()
        self.first_pokemon_in_box = self.rio["first_pokemon_in_box"]
        self.box_spacing = self.rio["box_spacing"]
        self.hatch_grid = self.rio["hatch_grid"]
        self.hatch_egg_button = self.rio["hatch_egg_button"]
        self.confirm_hatch_egg = self.rio["confirm_hatch_egg"]
        self.select_parent = self.rio["select_parent"]

    def select_pokemon_click(self,count,switch,button='left'):
        row = count // 10
        column = count % 10
        x = self.first_pokemon_in_box[0]+ column * self.box_spacing[0]
        y = self.first_pokemon_in_box[1]+ (row + switch * 3) * self.box_spacing[1]
        rio = [x,y,self.first_pokemon_in_box[2],self.first_pokemon_in_box[3]]
        self.click(rio,button)


    def select_parent_click(self):
        self.click(self.select_parent)

    def select_hatch_click(self):
        position = pydirectinput.position()
        roi = [position[0]+self.hatch_grid[0],position[1]+self.hatch_grid[1],self.hatch_grid[2],self.hatch_grid[3]]
        self.random_drift_prob = -1.0
        self.click(roi)
        self.random_drift_prob = self.rio["random_drift_prob"]

    def hatch_egg_button_click(self):
        self.click(self.hatch_egg_button)

    def confirm_hatch_egg_click(self):
        self.click(self.confirm_hatch_egg)



# import cv2
# import numpy as np
#
#
# def draw_pokemon_boxes(frame, mbox):
#     """
#     在图像上绘制所有宝可梦位置的红框
#     """
#     # 复制原图以避免修改原图
#     img_with_boxes = frame.copy()
#
#     # 绘制30个第一排宝可梦的位置
#     for i in range(30):
#         rio_1 = mbox.select_pokemon_click(i, 0)
#         draw_single_box(img_with_boxes, rio_1, f"P1-{i}")
#
#     # 绘制30个第二排宝可梦的位置
#     for i in range(30):
#         rio_2 = mbox.select_pokemon_click(i, 1)
#         draw_single_box(img_with_boxes, rio_2, f"P2-{i}")
#
#     return img_with_boxes
#
#
# def draw_single_box(img, rio, label=""):
#     """
#     绘制单个矩形框
#     rio格式: [x, y, width, height]
#     """
#     x, y, w, h = map(int, rio[:4])  # 确保坐标是整数
#
#     # 绘制红色矩形框 (BGR格式，红色是(0,0,255))
#     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
#
#     # 可选：添加标签
#     if label:
#         cv2.putText(img, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
#                     0.5, (0, 0, 255), 1, cv2.LINE_AA)
#
#
# def save_and_display_boxes(frame, mbox, output_path="pokemon_boxes.png"):
#     """
#     保存并显示带有框的图像
#     """
#     # 绘制所有框
#     result_img = draw_pokemon_boxes(frame, mbox)
#
#     # 保存图像
#     cv2.imwrite(output_path, result_img)
#     print(f"图像已保存到: {output_path}")
#
#     # 显示图像（可选）
#     cv2.imshow("Pokemon Boxes", result_img)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#
#     return result_img
#
#
# # 使用示例
# if __name__ == "__main__":
#     # 创建对象
#     mbox = MBox()
#     camera = Camera()
#
#     # 获取一帧图像
#     frame = camera.grab()
#
#     # 绘制所有框并保存
#     result_image = save_and_display_boxes(frame, mbox, "pokemon_boxes_60.png")
