"""
Input is group of motion corrected micrographs.
Output is group of icegrouped images.
"""
import os
import sys
import time
from multiprocessing import Pool

import cv2
import mrcfile
import numpy as np

#from icebreaker import KMeans_segmenter as KMeans_seg
#from icebreaker import filter_designer as fd
#from icebreaker import original_mask_fast as omf
#from icebreaker import window_mean as wm

import KMeans_segmenter as KMeans_seg
import filter_designer as fd
import original_mask_fast as omf
import window_mean as wm


def load_img(img_path):
    '''Loads mrc file using mrcfile library, returns image as a 2D array.

    Args:
        img_path(string): A path to an image(mrc file) 
    '''
    with mrcfile.open(img_path, "r", permissive=True) as mrc:
        img = mrc.data
        return img


def multigroup(filelist_full): #possibly rename to output handler or sth for clarity this is kept as separate funciton in case if in the future image segmenation parameters would be defined by users
    '''Defines the parameters for segmentation (number of patches and segments), calls the segmentation function, handles the output files, adding '_grouped.mrc' suffix to original name
 
    Args:
        filelist_full(list of strings): list containing paths to mrc files in a directory, created with main funtion
    '''

    img = load_img(filelist_full)
    splitpath = os.path.split(filelist_full)
    x_patches = 40
    y_patches = 40
    num_of_segments = 16
    final_image = ice_grouper(img, x_patches, y_patches, num_of_segments)

    with mrcfile.new(
        os.path.join(splitpath[0] + "/grouped/" + splitpath[1][:-4] + "_grouped_"+str(x_patches)+"x"+str(y_patches)+"x"+str(num_of_segments)+".mrc"),
        overwrite=True,
    ) as out_image:  
        out_image.set_data(final_image)


def ice_grouper(img, x_patches, y_patches, num_of_segments):
    '''Processes the image: average pooling, scaling, K-means segmentation. Average value from the original image is calculated for each segment idependently. Returns image as a 2D array of summed segments.  
    
    Args:
        img(2D array) - image to process
        x_patches(int) - number of patches in x direction of the image
        y_patches(int) - number of patches in y direction of the image
        num_of_segments(int) - desired number of groups for KMeans segmentation
    '''    

    rolled = wm.window(img, x_patches, y_patches)
    rolled_resized = cv2.resize(rolled, (int(rolled.shape[1]/20), int(rolled.shape[0]/20)), interpolation=cv2.INTER_AREA) #change to patches or fixed size?
    rolled_scaled = rolled_resized*10000
    KMeans_segmented = KMeans_seg.segmenter(rolled_scaled, num_of_segments)
    regions_vals = np.unique(KMeans_segmented)
    averaged_loc = np.zeros(
        (rolled_resized.shape[0], rolled_resized.shape[1], num_of_segments), np.float32
    )
    res = np.zeros((rolled_resized.shape[0], rolled_resized.shape[1]), np.float32)
    for i in range(len(regions_vals)):
        averaged_loc[:, :, i] = omf.original_mask(
            rolled_scaled, KMeans_segmented, regions_vals[i], rolled_resized, rolled
        )
        res[:, :] += averaged_loc[:, :, i]

    final_image = res

    return final_image


def main(indir, cpus):
    '''Gets the list of all .mrc files to process from the input directory, creates a subfolder for the output files, runs the image processing in parallel on multiple CPUs, prints total processing time
    
    Args:
        indir(string) - path to the folder containing input files
        cpus(int) - number of CPUs to use for parallel processing
    '''
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
        else:
            continue

    with Pool(cpus) as p:
        p.map(multigroup, filelist)

    print("------ %s sec------" % (time.time() - start_time))
    return True

if __name__ == "__main__":
    indir = sys.argv[1]
    batch_size = int(sys.argv[2])
    main(indir, batch_size)
