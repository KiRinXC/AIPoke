import cv2
from Camera import Camera
from get_tem import get_tem
camera = Camera()
frame = camera.grab()

# 截屏
# cv2.imwrite('frame.png', frame)


# # 截取一个区域
# x, y, w, h = 164,158,8,8
# roi = frame[y:y+h, x:x+w]
# cv2.imwrite('roi.png', roi)
#
# # 截取模板
region = [249,150,26,15]
template = get_tem(frame, region)
cv2.imwrite('select_parent.png', template)


