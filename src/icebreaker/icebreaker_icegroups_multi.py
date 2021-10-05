"""
Input is group of motion corrected micrographs.
Output is group of icegrouped images.
"""
import sys
import mrcfile
import cv2
import numpy as np
import os
import time


from multiprocessing import Pool

from icebreaker import filter_designer as fd
from icebreaker import window_mean as wm
from icebreaker import KNN_segmenter as KNN_seg
from icebreaker import original_mask_fast as omf


def load_img(img_path):
    with mrcfile.open(img_path, "r", permissive=True) as mrc:

        # mrc.header.map = mrcfile.constants.MAP_ID
        img = mrc.data
        return img


def multigroup(filelist_full):

    # for filename in filelist:
    img = load_img(filelist_full)
    splitpath = os.path.split(filelist_full)
    # print(splitpath[0])
    # Config params
    x_patches = 40
    y_patches = 40
    num_of_segments = 16

    final_image = ice_grouper(img, x_patches, y_patches, num_of_segments)
    # final_image = img  # !!!!! FOR TESTING

    # with mrcfile.new((path1+str(filename[:-4]) +'_'+str(x_patches)+
    # 'x'+str(y_patches)+'x'+str(num_of_segments)+'_original_mean'+'.mrc'),
    # overwrite=True) as out_image:
    with mrcfile.new(
        os.path.join(splitpath[0] + "/grouped/" + splitpath[1][:-4] + "_grouped.mrc"),
        overwrite=True,
    ) as out_image:  # Make fstring
        out_image.set_data(final_image)


def ice_grouper(img, x_patches, y_patches, num_of_segments):

    filter_mask = fd.lowpass(img, 0.85, 20, "cos", 50)
    lowpass, mag = fd.filtering(img, filter_mask)
    lowpass = cv2.GaussianBlur(lowpass, (45, 45), 0)
    lowpass12 = img
    rolled = wm.window(lowpass, x_patches, y_patches)
    rolled_resized = cv2.resize(rolled, (185, 190), interpolation=cv2.INTER_AREA)
    rolled_resized = cv2.GaussianBlur(rolled_resized, (5, 5), 0)
    KNNsegmented = KNN_seg.segmenter(rolled_resized, num_of_segments)
    # upscaled_region = cv2.resize(
    #    KNNsegmented, (lowpass.shape[1], lowpass.shape[0]), interpolation=cv2.INTER_AREA
    # )

    regions_vals = np.unique(KNNsegmented)
    averaged_loc = np.zeros(
        (lowpass.shape[0], lowpass.shape[1], num_of_segments), np.float32
    )
    res = np.zeros((lowpass.shape[0], lowpass.shape[1]), np.float32)
    for i in range(len(regions_vals)):
        averaged_loc[:, :, i] = omf.original_mask(
            lowpass, KNNsegmented, regions_vals[i], img, lowpass12
        )
        res[:, :] += averaged_loc[:, :, i]

    final_image = res

    return final_image


def main(indir, cpus):
    outdir = "grouped"
    path1 = os.path.join(indir, outdir)
    try:
        os.mkdir(path1)
    except OSError:
        print(f"Creation of the directory {path1} failed")
    else:
        print(f"Successfully created the directory {path1}")
    start_time = time.time()

    filelist = []
    for filename in os.listdir(indir):
        if filename.endswith(".mrc"):
            finalpath = os.path.join(indir, filename)
            filelist.append(finalpath)
            # print(filelist)
        else:
            continue

    # cc = 0

    with Pool(cpus) as p:
        p.map(multigroup, filelist)

    print("------ %s sec------" % (time.time() - start_time))

    return True


if __name__ == "__main__":
    indir = sys.argv[1]
    batch_size = sys.argv[2]
    main(indir, batch_size)
