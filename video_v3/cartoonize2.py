import cv2
import numpy as np

def cartoonize(id):
    img = cv2.imread(f'image_and_video/{id}.jpg')
    # 卡通化處理
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 7)

    color = cv2.bilateralFilter(img, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    cv2.imwrite(f'image_and_video/{id}-2.jpg', cartoon)

cartoonize(0)
