"""
Input is group of motion corrected micrographs.
Output is group of equalized images.
"""
import sys
import mrcfile
# import cv2
import numpy as np
import os

# import filter_designer as fd
# import window_mean as wm
# import local_mask as lm
# import KNN_segmenter as KNN_seg


def load_img(img_path):
    with mrcfile.open(img_path, 'r', permissive=True) as mrc:
        img = mrc.data
        return img


def equalize_im(img, x_patches, y_patches, num_of_segments):

    filter_mask = fd.lowpass(img, 0.85, 20, 'cos', 50)
    lowpass, mag = fd.filtering(img, filter_mask)
    lowpass = cv2.GaussianBlur(lowpass, (45, 45), 0)
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
                             num_of_segments), np.uint8)
    res = np.zeros((lowpass.shape[0], lowpass.shape[1]), np.uint8)
    for i in range (len(regions_vals)):
        averaged_loc[:, :, i] = lm.local_mask(lowpass, KNNsegmented,
                                              regions_vals[i])
        res[:, :] += averaged_loc[:, :, i]
        final_image = cv2.GaussianBlur(res, (45, 45), 0)

    return final_image


def main(indir):
    outdir = 'flattened'
    path1 = os.path.join(indir, outdir)

    try:
        os.mkdir(path1)
    except OSError:
        print(f"Creation of the directory {path1} failed")
    else:
        print(f"Successfully created the directory {path1}")

    filelist = []
    for filename in os.listdir(indir):
        if (filename.endswith(".mrc")):
            filelist.append(filename)
        else:
            continue

    cc = 0
    for filename in filelist:
        img = load_img(os.path.join(indir, filename))

        # Config params
        x_patches = 40
        y_patches = 40
        num_of_segments = 32

        # final_image = equalize_im(img, x_patches, y_patches, num_of_segments)
        final_image = img  # !!!! TESTING

        #with mrcfile.new((path1+str(filename[:-4]) +'_'+str(x_patches)+'x'+str(y_patches)+'x'+str(num_of_segments)+'flattened'+'.mrc'), overwrite=True) as out_image:    # Make fstring
        with mrcfile.new(os.path.join(path1, filename[:-4] + f'_{outdir}.mrc'), overwrite=True) as out_image:    # Make fstring
            out_image.set_data(final_image)

        cc += 1
        print(f'{cc}/{len(filelist)}')

    return True


if __name__ == '__main__':
    indir = sys.argv[1]
    main(indir)
