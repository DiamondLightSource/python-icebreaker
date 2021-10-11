import numpy as np
import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D


def show_gradient(image):
    xx, yy = np.mgrid[0: image.shape[0], 0: image.shape[1]]
    fig = plt.figure(figsize=(15, 15))
    ax = fig.gca(projection="3d")
    ax.plot_surface(xx, yy, image, rstride=1, cstride=1, cmap=plt.cm.gray, linewidth=2)
    ax.view_init(80, 30)
    plt.show()
