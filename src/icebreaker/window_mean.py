import numpy as np


def window(img, x_patches, y_patches):
    rows, cols = img.shape
    x_patch_size = int(cols / x_patches)
    y_patch_size = int(rows / y_patches)
    mean_map = img.copy()
    for i in range(x_patches):
        for j in range(y_patches):
            if i == x_patches - 1 and j != y_patches - 1:
                mean_map[
                    (j * y_patch_size): ((j + 1) * y_patch_size), (i * x_patch_size):
                ] = np.mean(
                    mean_map[
                        (j * y_patch_size): ((j + 1) * y_patch_size),
                        (i * x_patch_size):,
                    ]
                )
            elif j == y_patches - 1 and i != x_patches - 1:
                mean_map[
                    (j * y_patch_size):, (i * x_patch_size): ((i + 1) * x_patch_size)
                ] = np.mean(
                    mean_map[
                        (j * y_patch_size):,
                        (i * x_patch_size): ((i + 1) * x_patch_size),
                    ]
                )
            elif j == y_patches - 1 and i == x_patches - 1:
                mean_map[(j * y_patch_size):, (i * x_patch_size):] = np.mean(
                    mean_map[(j * y_patch_size):, (i * x_patch_size):]
                )
            else:
                mean_map[
                    (j * y_patch_size): ((j + 1) * y_patch_size),
                    (i * x_patch_size): ((i + 1) * x_patch_size),
                ] = np.mean(
                    mean_map[
                        (j * y_patch_size): ((j + 1) * y_patch_size),
                        (i * x_patch_size): ((i + 1) * x_patch_size),
                    ]
                )

    return mean_map
