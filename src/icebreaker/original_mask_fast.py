import cv2
import numpy as np
# import matplotlib.pyplot as plt
# import mrcfile


def original_mask(lowpass1, img2, val, original, lowpass12):
    reg3 = np.ones((img2.shape[0], img2.shape[1]), np.uint8)
    # orig_mean = np.zeros((lowpass12.shape[0], lowpass12.shape[1]), np.float32)
    # coord0 = []
    # coord1 = []
    # global_mean = np.mean(lowpass12)
    # k = np.zeros((img2.shape[0], img2.shape[1]), np.uint8)
    for u in range(img2.shape[0]):
        for v in range(img2.shape[1]):
            if img2[u, v] == val:
                reg3[u, v] = 1
            else:
                reg3[u, v] = 0

    up_reg3 = cv2.resize(
        reg3, (lowpass1.shape[1], lowpass1.shape[0]), interpolation=cv2.INTER_NEAREST
    )
    # mean_vals = cv2.mean(lowpass1, up_reg3)[0]
    up_reg3 = up_reg3 * lowpass1
    x_mean = np.mean(original[np.nonzero(up_reg3)])

    # Negative of ROI
    # cover3 = 1 - reg3

    # Upscaled negative
    up_reg3 = cv2.resize(
        reg3, (lowpass1.shape[1], lowpass1.shape[0]), interpolation=cv2.INTER_NEAREST
    )
    orig_mean = up_reg3 * x_mean
    return orig_mean
