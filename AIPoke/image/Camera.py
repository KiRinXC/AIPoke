import dxcam
class Camera(object):
    def __init__(self):
        self.camera = dxcam.create(output_idx=0, output_color="BGR")
        self.region = (0, 0, 1100, 900)

        self.camera.start(target_fps=10,region=self.region)  # 返回 numpy array (H, W, 3) BGR 格式

    def grab(self):
        frame = self.camera.get_latest_frame()
        return frame

# import cv2
# camera = Camera()
# frame = camera.grab()
# # 要框的区域
# x, y, w, h = 164,158,8,8
# # cv2.imwrite("test7.png", frame)
#
# # ① 只截子图w
# roi = frame[y:y+h, x:x+w]
# from get_tem import get_tem
# tem = get_tem(frame,[517,340,19,18])
# cv2.imwrite("pokedex.png", tem)
#
# # ② 在原图上画框
# cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
#
# # 看看效果
# cv2.imshow("frame", frame)
# # cv2.imshow("roi", roi)
# cv2.waitKey(0)
# cv2.destroyAllWindows()