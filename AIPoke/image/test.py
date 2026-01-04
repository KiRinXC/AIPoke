import cv2
import numpy as np
# frame = cv2.imread('2025-4-9-19-21.png')
frame = cv2.imread('full_image.png')

# 1. 设定区域（左上角 x,y 和宽高）
x, y, w, h = 100, 500, 10, 10

# 2. 画红线框（BGR 顺序，红=0,0,255）
# cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

# 3. 直接切片取出这块区域
roi = frame[y:y+h, x:x+w]

# 想看结果
# cv2.imshow('frame', frame)
cv2.imshow('roi', roi)
cc = np.max(roi, axis=-1)
print(cc)
cv2.waitKey(0)
cv2.destroyAllWindows()