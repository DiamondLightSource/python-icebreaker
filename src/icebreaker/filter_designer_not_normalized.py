import mrcfile
import cv2
import numpy as np
import matplotlib.pyplot as plt


def load_img(img_path):
    with mrcfile.open(img_path, "r+") as mrc:
        img = mrc.data
        plt.imshow(img, cmap="gray")
        plt.show()
        return img


def lowpass(img, pixel_size, lowcut, edge_type, falloff, lowpass=True):
    mask_rad = int((pixel_size / lowcut) * (img.shape[1]))
    rows, cols = img.shape
    crow, ccol = int(rows / 2), int(cols / 2)  # center

    filter = np.zeros((rows, cols, 2), np.float32)
    f_mask = np.zeros((rows, cols), np.float32)

    mask = cv2.circle(f_mask, (ccol, crow), mask_rad, (1), -1)

    if edge_type == "cos":
        for i in range(falloff):
            mask_edge = cv2.circle(
                mask,
                (ccol, crow),
                mask_rad + i,
                (np.cos(i * ((3.14 * 0.5) / falloff))),
                2,
            )
    elif edge_type == "linear":
        for i in range(falloff):
            mask_edge = cv2.circle(
                mask, (ccol, crow), mask_rad + i, (1 - i * (1 / falloff)), 2
            )
    else:
        mask_edge = mask
    filter[:, :, 0] = mask_edge
    filter[:, :, 1] = mask_edge
    if lowpass is False:
        filter = 1 - filter
    # print(img.shape)
    # print(filter.shape)
    return filter


def bandpass(
    img,
    pixel_size,
    lowcut,
    highcut,
    edge_type,
    falloff_in,
    falloff_out=1,
    bandpass_type=True,
):
    mask_rad_in = int((pixel_size / lowcut) * (img.shape[1])) - falloff_in
    mask_rad_out = int((pixel_size / highcut) * (img.shape[1]))
    rows, cols = img.shape
    crow, ccol = int(rows / 2), int(cols / 2)  # center
    filter = np.zeros((rows, cols, 2), np.float32)

    #mask_bandpass = np.zeros((rows, cols, 2), np.float32)

    maskin = np.zeros((rows, cols), np.float32)
    maskout = np.zeros((rows, cols), np.float32)

    bandpass_out = cv2.circle(maskout, (ccol, crow), mask_rad_out, (1), -1)
    bandpass_in = cv2.circle(maskin, (ccol, crow), mask_rad_in, (1), -1)

    if edge_type == "cos":
        for i in range(falloff_out):
            bandpass_out = cv2.circle(
                bandpass_out,
                (ccol, crow),
                mask_rad_out + i,
                (np.cos(i * ((3.14 * 0.5) / falloff_out))),
                2,
            )
        for i in range(falloff_in):
            bandpass_in = cv2.circle(
                bandpass_in,
                (ccol, crow),
                mask_rad_in + i,
                (np.cos(i * ((3.14 * 0.5) / falloff_in))),
                2,
            )

    elif edge_type == "linear":
        for i in range(falloff_out):
            bandpass_out = cv2.circle(
                bandpass_out,
                (ccol, crow),
                mask_rad_out + i,
                (1 - i * (1 / falloff_out)),
                2,
            )
        for i in range(falloff_in):
            bandpass_in = cv2.circle(
                bandpass_in,
                (ccol, crow),
                mask_rad_in + i,
                (1 - i * (1 / falloff_in)),
                2,
            )

    else:
        bandpass = bandpass_out * (1 - bandpass_in)

    bandpass = bandpass_out * (1 - bandpass_in)

    filter[:, :, 0] = bandpass
    filter[:, :, 1] = bandpass
    if bandpass_type is False:
        filter = 1 - filter
    return filter


def filtering(img, filter_type):
    img_float32 = np.float32(img)
    dft = cv2.dft(img_float32, flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    fshift = dft_shift * (filter_type)
    f_ishift = np.fft.ifftshift(fshift)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
    #b0 = str(np.max(img))
    #b01 = str(np.mean(img))
    #b02 = str(np.min(img))

    #b1 = str(np.max(img_back))
    #b12 = str(np.mean(img_back))
    #b2 = str(np.min(img_back))
    # cv2.normalize(img_back,  img_back, 0.0, 255.0, cv2.NORM_MINMAX)
    # img_back = img_back.astype(np.uint8)
    # cv2.equalizeHist(img_back,img_back)
    magnitude_spectrum = 20 * np.log(
        cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]) + 1
    )
    # print(b0+'\t'+ b01 + '\t'+ b02+ '\t'+ b1+ '\t'+ b12 +'\t'+ b2 )
    # cv2.normalize(img_back,  img_back, 5.0, 30.0, cv2.NORM_MINMAX)
    return img_back, magnitude_spectrum
