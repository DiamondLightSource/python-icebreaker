'''
Equalize contrast locally based on the KMeans defined image areas
'''
import cv2
import numpy as np


def local_mask(img, img2, val):
    '''Defines local mask corresponding to the area defined by a single segment from KMeans clustering. Applies histogram equalization only to that area and returns it for full image reconstruction.

    Args:
        img(2D array) - original images used to upscale the local mask
        img2(2D array) - output image from KMeans processing
        val(int) - id of the single cluster from KMeans processing
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

    mask3 = cv2.equalizeHist(up_reg3)

    return mask3
