from detect.detect import det_escape,det_nickname
from image.init_cam import init_cam

try:
    camera = init_cam()
    while True:
        # 1. 获取完整大图


        # while True:
        frame = camera.get_latest_frame()
        # ================= 核心操作 =================
        battle = det_nickname(frame)
        escape = det_escape(frame)
        print(f"遇怪中: {battle}\t可逃跑: {escape}")

except KeyboardInterrupt:
    pass

