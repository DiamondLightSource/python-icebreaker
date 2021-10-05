import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mrcfile
import cv2
import os
import seaborn as sns


def main(mic_path):
    orig_stdout = sys.stdout
    indir = mic_path
    f = open("five_figs_test.csv", "w")
    sys.stdout = f
    files = []
    for filename in os.listdir(indir):
        if filename.endswith(".mrc"):
            finalpath = os.path.join(indir, filename)
            files.append(finalpath)
        else:
            continue
    # files = files.sort()
    files = sorted(files)
    vector_data = []
    r = 10000

    print("path,", "min,", "q1,", "q2=median,", "q3,", "max")
    for img_path in files:
        with mrcfile.open(img_path, "r", permissive=True) as mrc:
            img = mrc.data
            if np.isnan(np.sum(img)):
                continue
            else:
                print(
                    img_path[:-4] + ",",
                    str(int(np.min(img) * r)) + ",",
                    str(int(np.quantile(img, 0.25) * r)) + ",",
                    str(int(np.median(img) * r)) + ",",
                    str(int(np.quantile(img, 0.75) * r)) + ",",
                    int(np.max(img) * r),
                )

    sys.stdout = orig_stdout
    f.close()


if __name__ == "__main__":
    mic_path = sys.argv[1]
    main(mic_path)
