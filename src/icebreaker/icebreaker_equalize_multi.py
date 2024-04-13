"""
Input is group of motion corrected micrographs.
Output is group of equalized images.
"""

import os
import sys
from multiprocessing import Pool

import cv2
import mrcfile
import numpy as np

from icebreaker import KMeans_segmenter as KMeans_seg
from icebreaker import filter_designer as fd
from icebreaker import local_mask as lm
from icebreaker import window_mean as wm

#import KMeans_segmenter as KMeans_seg
#import filter_designer as fd
#import local_mask as lm
#import window_mean as wm


def load_img(img_path):
    '''Loads mrc file using mrcfile library, returns image as a 2D array.

    Args:
        img_path(string): A path to an image(mrc file) 
    '''

    with mrcfile.open(img_path, "r", permissive=True) as mrc:
        img = mrc.data
        return img

def multigroup(filelist_full):
    '''Defines the parameters for segmentation (number of patches and segments), calls the segmentation function, handles the output files, adding '_flattened.mrc' suffix to original name
 
    Args:
        filelist_full(list of strings): list containing paths to mrc files in a directory, created with main funtion
    '''
    
    # for filename in filelist:
    img = load_img(filelist_full)  # (os.path.join(indir, filename))
    splitpath = os.path.split(filelist_full)
    # Config params
    x_patches = 40
    y_patches = 40
    num_of_segments = 32

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


def equalize_im(img, x_patches, y_patches, num_of_segments): 
    '''Processes the image: average pooling, scaling, K-means segmentation. Histogram equalization is performed for each segment idependently. Returns image as a 2D array of summed segments.      
    
    Args:
        img(2D array) - image to process
        x_patches(int) - number of patches in x direction of the image
        y_patches(int) - number of patches in y direction of the image
        num_of_segments(int) - desired number of groups for KMeans segmentation
    '''
    filter_mask = fd.lowpass(img, 1, 20, "cos", 50)
    lowpass, mag = fd.filtering(img, filter_mask)
    #lowpass = cv2.GaussianBlur(lowpass, (45, 45), 0)
    rolled = wm.window(lowpass, x_patches, y_patches)
    rolled_resized = cv2.resize(rolled, (185, 190), interpolation=cv2.INTER_NEAREST)
    #rolled_resized = cv2.GaussianBlur(rolled_resized, (5, 5), 0)
    KNNsegmented = KMeans_seg.segmenter(rolled_resized, num_of_segments)

    # upscaled_region = cv2.resize(
    # KNNsegmented, (lowpass.shape[1], lowpass.shape[0]), interpolation=cv2.INTER_AREA)

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
    '''Gets the list of all .mrc files to process from the input directory, creates a subfolder for the output files, runs the image processing in parallel on multiple CPUs
     
    Args:
        indir(string) - path to the folder containing input files
        cpus(int) - number of CPUs to use for parallel processing
    '''
    outdir = "flattened"
    path1 = os.path.join(indir, outdir)

    try:
        os.mkdir(path1)
    except OSError:
        print(f"Creation of the directory {path1} failed")
    else:
        print(f"Successfully created the directory {path1}")

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

    return True


if __name__ == "__main__":
    indir = sys.argv[1]
    batch_size = sys.argv[2]
    main(indir, batch_size)
