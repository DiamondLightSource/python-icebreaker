import cv2
import numpy as np
import matplotlib.pyplot as plt


def local_mask(lowpass1, img2, val):
    reg3 = np.ones((img2.shape[0], img2.shape[1]), np.uint8)
    coord0 = []
    coord1 = []
    k = np.zeros((img2.shape[0], img2.shape[1]), np.uint8)
    for u in range(img2.shape[0]):
        for v in range(img2.shape[1]):
            if img2[u, v] == val:
                reg3[u, v] = 1
            else:
                reg3[u, v] = 0

    up_reg3 = cv2.resize(
        reg3, (lowpass1.shape[1], lowpass1.shape[0]), interpolation=cv2.INTER_NEAREST
    )
    mean_vals = cv2.mean(lowpass1, up_reg3)[0]
    up_cover4 = up_reg3
    up_reg3 = up_reg3 * lowpass1
    # Negative of ROI
    cover3 = 1 - reg3
    # Upscaled negative
    up_cover3 = cv2.resize(cover3, (lowpass1.shape[1], lowpass1.shape[0]))

    mask3 = cv2.equalizeHist(up_reg3)

    return mask3
