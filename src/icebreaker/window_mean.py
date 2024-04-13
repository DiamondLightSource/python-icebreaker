'''
Script for average pooling of individual micrographs.
'''

import numpy as np


def window(img, x_patches, y_patches):
    '''Calculates average value inside each non-overlapping moving window. Returns image of the same size as input, but with the superpixels containing average value for each defined patch in x and y direction.

    Args:
        img(2D array) - current micrograph for processing
        x_patches(int) - requested number of patches in x direction of the micrograph
        y_patches(int) - requested number of patches in y direction of the micrograph
    '''
    rows, cols = img.shape
    x_patch_size = int(cols / x_patches)
    y_patch_size = int(rows / y_patches)
    mean_map = img.copy()
    for i in range(x_patches):
        for j in range(y_patches):
            if i == x_patches - 1 and j != y_patches - 1:
                mean_map[
                    (j * y_patch_size) : ((j + 1) * y_patch_size), (i * x_patch_size) :
                ] = np.mean(
                    mean_map[
                        (j * y_patch_size) : ((j + 1) * y_patch_size),
                        (i * x_patch_size) :,
                    ]
                )
            elif j == y_patches - 1 and i != x_patches - 1:
                mean_map[
                    (j * y_patch_size) :, (i * x_patch_size) : ((i + 1) * x_patch_size)
                ] = np.mean(
                    mean_map[
                        (j * y_patch_size) :,
                        (i * x_patch_size) : ((i + 1) * x_patch_size),
                    ]
                )
            elif j == y_patches - 1 and i == x_patches - 1:
                mean_map[(j * y_patch_size) :, (i * x_patch_size) :] = np.mean(
                    mean_map[(j * y_patch_size) :, (i * x_patch_size) :]
                )
            else:
                mean_map[
                    (j * y_patch_size) : ((j + 1) * y_patch_size),
                    (i * x_patch_size) : ((i + 1) * x_patch_size),
                ] = np.mean(
                    mean_map[
                        (j * y_patch_size) : ((j + 1) * y_patch_size),
                        (i * x_patch_size) : ((i + 1) * x_patch_size),
                    ]
                )

    return mean_map
