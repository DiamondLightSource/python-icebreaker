import cv2
import numpy as np
#import matplotlib.pyplot as plt
# import mrcfile
#from time import time

def new_original_mask(lowpass1, img2, val, original, lowpass12):
    reg3 = np.ones((img2.shape[0], img2.shape[1]), np.uint8)
    reg3 = np.where(img2 == val, 1.0, 0.0)

    up_reg_ref = reg3.copy()
    up_reg3 = reg3 * lowpass1
    x_mean = np.mean(original[np.nonzero(reg3)])
    orig_mean = up_reg_ref * x_mean

    return orig_mean

