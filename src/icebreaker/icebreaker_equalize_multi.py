"""
Input is group of motion corrected micrographs.
Output is group of equalized images.
"""

import sys
import mrcfile
import cv2
import numpy as np
import os
from multiprocessing import Pool

from icebreaker import filter_designer as fd
from icebreaker import window_mean as wm
from icebreaker import local_mask as lm
from icebreaker import KNN_segmenter as KNN_seg
import time

from sklearn.cluster import KMeans

def load_img(img_path):
    with mrcfile.open(img_path, "r", permissive=True) as mrc:
        img = mrc.data
        return img


def multigroup(filelist_full):

    # for filename in filelist:
    img = load_img(filelist_full)  # (os.path.join(indir, filename))
    splitpath = os.path.split(filelist_full)
    # Config params
    x_patches = 40
    y_patches = 40
    num_of_segments = 8

    final_image = equalize_im(img, x_patches, y_patches, num_of_segments)
    # final_image = img  # !!!! TESTING

    # with mrcfile.new((path1+str(filename[:-4]) +'_'
    # +str(x_patches)+'x'+str(y_patches)+'x'+str(num_of_segments)+'flattened'+'.mrc'),
    # overwrite=True) as out_image:    # Make fstring
    with mrcfile.new(
        os.path.join(
            splitpath[0] + "/flattened/" + splitpath[1][:-4] + "_flattened.mrc"
        ),
        overwrite=True,
    ) as out_image:  # Make fstring
        out_image.set_data(final_image)

def recreate_image(codebook, labels, w, h):
    ##"""Recreate the (compressed) image from the code book & labels"""
    return codebook[labels].reshape(w, h)

def equalize_im(img, x_patches, y_patches, num_of_segments):

    lowpass = img
    rolled = wm.window(lowpass, x_patches, y_patches)
    rolled_resized = cv2.resize(rolled, (185, 190), interpolation=cv2.INTER_NEAREST)
    rolled_resized = cv2.GaussianBlur(rolled_resized, (5, 5), 0)
    a = np.reshape(rolled_resized, (185*190, -1))

    ##b = cudf.DataFrame(a)
    ##kmeans_float = KMeans(n_clusters=num_of_segments,max_iter=300,random_state=0,output_type='numpy')
    kmeans_float = KMeans(n_clusters=num_of_segments,init='k-means++',random_state=0,max_iter = 300)
    labels=kmeans_float.fit_predict(a)

    KNNsegmented=recreate_image(kmeans_float.cluster_centers_, labels, 190, 185)

    upscaled_region = cv2.resize(KNNsegmented, (lowpass.shape[1], lowpass.shape[0]), interpolation=cv2.INTER_AREA)

    regions_vals = np.unique(KNNsegmented)
    averaged_loc = np.zeros(
        (lowpass.shape[0], lowpass.shape[1], num_of_segments), np.uint8
    )
    res = np.zeros((lowpass.shape[0], lowpass.shape[1]), np.uint8)
    for i in range(len(regions_vals)):
        averaged_loc[:, :, i] = lm.local_mask(lowpass, KNNsegmented, regions_vals[i])
        res[:, :] += averaged_loc[:, :, i]
    
    final_image = res  # cv2.GaussianBlur(res, (45, 45), 0)
    return final_image


def main(indir, cpus):
    outdir = "flattened"
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
        else:
            continue

    # cc = 0
    # for filename in filelist:
    #    img = load_img(os.path.join(indir, filename))

    # Config params
    #    x_patches = 40
    #    y_patches = 40
    #    num_of_segments = 32

    #    final_image = equalize_im(img, x_patches, y_patches, num_of_segments)
    # final_image = img  # !!!! TESTING

    # with mrcfile.new((path1+str(filename[:-4]) +'_'+str(x_patches)+'x'+str(y_patches)+
    # 'x'+str(num_of_segments)+'flattened'+'.mrc'), overwrite=True) as out_image:
    # Make fstring
    #   with mrcfile.new(os.path.join(path1, filename[:-4] + f'_{outdir}.mrc'),
    #   overwrite=True) as out_image:    # Make fstring
    #     out_image.set_data(final_image)

    # cc += 1
    # print(f'{cc}/{len(filelist)}')
    with Pool(cpus) as p:
        p.map(multigroup, filelist)
    print("------ %s sec------" % (time.time() - start_time))

    return True


if __name__ == "__main__":
    indir = sys.argv[1]
    batch_size = sys.argv[2]
    main(indir, batch_size)
