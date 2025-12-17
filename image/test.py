from init_cam import init_cam
from get_tem import get_tem
from color import has_white_pix
import cv2

# # 1. 获取完整大图
# camera = init_cam()
#
#
# # while True:
# frame = camera.get_latest_frame()
# # ================= 核心操作 =================
#
# region = [473,640,27,12]
# roi = frame[region[1]:region[1]+region[3],region[0]:region[0]+region[2]]
#
# # 保存看看对不对
# cv2.imwrite("full_image.png", frame)  # 保存原图
# cv2.imwrite("roi_crop.png", roi)  # 保存截取的小图
#
#
# region = [473, 640, 27, 12]
# binary_roi = get_tem(frame, region)
# cv2.imwrite("../data/TEM/escape.png", binary_roi)
# camera.stop()

from match_tem import verify_area
from image.color import has_white_pix
from image.match_tem import match_static,match_dynamic
from utili.tem_manager import load_all_templates
from utili.path_manager import TEM_DIR

rio_dict={
    "nickname":[570,409,20,10],
    "escape":[473, 640, 27, 12]
}

tem_dict = load_all_templates(template_dir=TEM_DIR)


img_dir = r"2025-4-9-19-21.png"
region = [473,640,27,12]
flag = verify_area(img_dir,region,tem_dict["escape"])
print(flag)