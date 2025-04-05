import numpy as np
import cv2

def edge(img):
    origine = img
    siz = min(img.shape[:2])
    print(siz*0.0005)
    blur_kernel = int(siz*0.0005)
    print(blur_kernel)
    #origine = cv2.blur(origine,(blur_kernel,blur_kernel))
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #img = 255 - img
    #img = cv2.blur(img, (8, 8))
    #img = cv2.equalizeHist(img)
    img = cv2.GaussianBlur(img, (7, 7), 0)
    cv2.imwrite("blured.png",img)
    edges = cv2.adaptiveThreshold(img, 255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY, 11, 7)
    cv2.imwrite("edge_only.png",edges)
    mask = cv2.inRange(edges, 255, 255) # bgrからマスクを作成
    extract = cv2.bitwise_and(origine, origine, mask=mask) # 元画像とマスクを合成
    #cv2.imwrite("dst.png", dst)
    #cv2.imwrite("extract.png",extract)
    print(img.shape)
    return extract
cv2.imwrite("edge_result.png",edge(cv2.imread("image.png")))

