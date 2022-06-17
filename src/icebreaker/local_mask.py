import cv2
import numpy as np


def local_mask(lowpass1, img2, val):
    reg3 = np.ones((img2.shape[0], img2.shape[1]), np.uint8)
    reg3 = np.where(img2 == val, 1.0, 0.0)    

    up_reg3 = cv2.resize(
        reg3, (lowpass1.shape[1], lowpass1.shape[0]), interpolation=cv2.INTER_NEAREST
    )
    up_reg3 = up_reg3 * lowpass1
    up_reg3=cv2.normalize(up_reg3,None, 0.0, 255.0, cv2.NORM_MINMAX, cv2.CV_8UC1)
    mask3 = cv2.equalizeHist(up_reg3)

    return mask3
