"""
Input is group of motion corrected micrographs.
Output is group of icegrouped images.
"""
import sys
import mrcfile
import cv2
import numpy as np
import os
import ndimage

import filter_designer as fd
import window_mean as wm
import KNN_segmenter as KNN_seg
import original_mask as om


def load_img(img_path):
    with mrcfile.open(img_path, 'r', permissive=True) as mrc:
        img = mrc.data
        return img


def ice_grouper(img, x_patches, y_patches, num_of_segments):

    filter_mask = fd.lowpass(img, 0.85, 20, 'cos', 50)
    lowpass, mag = fd.filtering(img, filter_mask)
    lowpass = cv2.GaussianBlur(lowpass, (45, 45), 0)
    lowpass12 = img
    rolled = wm.window(lowpass, x_patches, y_patches)
    rolled_resized = cv2.resize(rolled, (185, 190),
                                interpolation=cv2.INTER_AREA)
    rolled_resized = cv2.GaussianBlur(rolled_resized, (5, 5), 0)
    KNNsegmented = KNN_seg.segmenter(rolled_resized, num_of_segments)
    upscaled_region = cv2.resize(KNNsegmented,
                                 (lowpass.shape[1], lowpass.shape[0]),
                                 interpolation=cv2.INTER_AREA)

    regions_vals = np.unique(KNNsegmented)
    averaged_loc = np.zeros((lowpass.shape[0], lowpass.shape[1],
                             num_of_segments), np.float32)
    res = np.zeros((lowpass.shape[0], lowpass.shape[1]), np.float32)
    for i in range (len(regions_vals)):
            averaged_loc[:, :, i] = om.original_mask(lowpass,
                                                     KNNsegmented,
                                                     regions_vals[i],
                                                     img, lowpass12)
            res[:, :] += averaged_loc[:, :, i]

    final_image = ndimage.median_filter(res, size=10)

    return final_image


def main(indir):
    outdir = 'icegroups/'
    path1 = indir+outdir
    try:
        os.mkdir(path1)
    except OSError:
        print("Creation of the directory %s failed" % path1)
    else:
        print("Successfully created the directory %s " % path1)

    filelist = []
    for filename in os.listdir(indir):
        if (filename.endswith(".mrc")):
            filelist.append(filename)
        else:
            continue

    cc = 0
    for filename in filelist:
        img = load_img(indir+filename)

        # Config params
        x_patches = 40
        y_patches = 40
        num_of_segments = 16

        final_image = ice_grouper(img, x_patches, y_patches, num_of_segments)


        with mrcfile.new((path1+str(filename[:-4]) +'_'+str(x_patches)+'x'+str(y_patches)+'x'+str(num_of_segments)+'_original_mean'+'.mrc'), overwrite=True) as out_image:
            out_image.set_data(final_image)

        cc += 1
        print(f'{cc}/{len(filelist)}')

    return True

if __name__ == '__main__':
    indir = sys.argv[1]
    main(indir)
