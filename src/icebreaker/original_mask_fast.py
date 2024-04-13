'''
Script for calculating mean values from the original input micrographs in the areas defined by KMeans clustering
'''
import cv2
import numpy as np


def original_mask(img, img2, val, original, lowpass12):
    '''Defines local mask corresponding to the area defined by a single segment from KMeans clustering. Calculates average value from the original input micrograph only in that area and returns it for full image reconstruction.

    Args:
        img(2D array) - images wit the original input size used to upscale the local mask
        img2(2D array) - output image from KMeans processing
        val(int) - id of the single cluster from KMeans processing
        original(2D array) - original input micrograph from which the average values are calculated
    '''
    reg3 = np.ones((img2.shape[0], img2.shape[1]), np.uint8)
    for u in range(img2.shape[0]):
        for v in range(img2.shape[1]):
            if img2[u, v] == val:
                reg3[u, v] = 1
            else:
                reg3[u, v] = 0

    up_reg3 = cv2.resize(
        reg3, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST
    )
    up_reg3 = up_reg3 * img
    x_mean = np.mean(original[np.nonzero(up_reg3)])

    # Negative of ROI
    # cover3 = 1 - reg3

    # Upscaled negative
    up_reg3 = cv2.resize(
        reg3, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST
    )
    orig_mean = up_reg3 * x_mean
    return orig_mean
