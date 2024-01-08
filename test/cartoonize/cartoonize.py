import cv2
import numpy as np

def cartoonize(id):
    img = cv2.imread(f'image_and_video/{id}.jpg')

    # edge mask generation
    line_size = 7
    blur_value = 7

    gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray_blur = cv2.medianBlur(gray_img, blur_value)
    edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, line_size, blur_value)



    # Transform the image
    data = np.float32(img).reshape((-1, 3))

    # Determine criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)

    # Implementing K-Means
    k = 10
    ret, label, center = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    img_reduced = center[label.flatten()]
    img_reduced = img_reduced.reshape(img.shape)


    # Bilateral Filter

    blurred = cv2.bilateralFilter(img_reduced, d=7, sigmaColor=200,sigmaSpace=200)
    cartoon = cv2.bitwise_and(blurred, blurred, mask=edges)

    cv2.imwrite(f'image_and_video/{id}-1.jpg', cartoon)
    
cartoonize(2)