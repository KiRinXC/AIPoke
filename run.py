from image.Camera import Camera
from detect.Detect import Detect
import time
detect = Detect()
camera = Camera()

try:
    while True:
        frame = camera.grab()
        if frame is not None:
            # 检测撞墙
            obs_status = detect.det_obs(frame)

            # 打印结果
            # print(obs_status)
            for k,v in obs_status.items():
                if v:
                    print(k+" ",end="")
            print("\n++++++++")
        # time.sleep(0.)  # 模拟移动间隔

except KeyboardInterrupt:
    pass