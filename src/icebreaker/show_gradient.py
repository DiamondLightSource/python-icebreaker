'''
Shows 3D representation of the ice profile based on a micrograph generated with the 'group' mode
'''
import numpy as np
import matplotlib.pyplot as plt
import sys
import mrcfile

img_path = sys.argv[1]
with mrcfile.open(img_path, "r", permissive=True) as mrc:
    image = mrc.data

print(image.shape)


def show_gradient(image):
    xx, yy = np.mgrid[0 : image.shape[0], 0 : image.shape[1]]
    fig = plt.figure(figsize=(10, 10))
    ax = fig.gca(projection="3d")
    ax.plot_surface(xx, yy, image, rstride=1, cstride=1, cmap=plt.cm.gray, linewidth=2)
    ax.view_init(30, 80)
    plt.show()

show_gradient(image)
