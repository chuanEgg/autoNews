import cv2
import numpy as np

def cartoonize_video(input_file, output_file):
    # 讀取影片
    cap = cv2.VideoCapture(input_file)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 創建影片寫入器
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 卡通化處理
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

        color = cv2.bilateralFilter(frame, 9, 300, 300)
        cartoon = cv2.bitwise_and(color, color, mask=edges)

        # 寫入影片
        out.write(cartoon)

        # # 顯示卡通化影片
        # cv2.imshow('Cartoonize', cartoon)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    # 釋放資源
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# 輸入和輸出檔案名稱
input_video = 'image_and_video/7.mp4'
output_video = 'image_and_video/7.avi'

# 調用函數
cartoonize_video(input_video, output_video)
