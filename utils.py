import numpy as np
import cv2
import math
import matplotlib.pyplot as plt
from joblib import Parallel, delayed


# Resize a image to maxSize on which ever dimention is higher in the original image
# Works for both 2d and 3d
def resizeImage(image, maxSize):
    (h, w) = image.shape[:2]

    if h > w:
        r = maxSize / float(h)
        dim = (int(w * r), maxSize)
    else:
        r = maxSize / float(w)
        dim = (maxSize, int(h * r))
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)


# Display the image
def displayImage(image, cm=-1):
    if cm != -1:
        plt.imshow(image, cmap=cm)
    else:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.imshow(image)
    plt.show()
    return None


# Normalize image to 0 - 255. Good for displaying.
def normalizeImage(image):
    return ((image - image.min()) / (image.max() - image.min())) * 255


# Returns a 1D Gausian filter with stdev = sigma and extention from (-ext * stdev) to (+ext * stdev)
def getGaussianFilter(sigma, ext):
    res = []
    for i in range(-int(ext * sigma), int(ext * sigma) + 1):
        s = (1 / (math.sqrt(2 * math.pi) * sigma))
        s *= math.exp(-(i * i) / (2 * sigma * sigma))
        res.append(s)

    return np.reshape(np.array(res), (np.array(res).shape[0], 1))


# Perform cross correlation in 2D on img with filter. Starting at 0,0 without any padding, so result will have a smaller size
def cross_correlation2d(filter, img):
    (fh, fw) = filter.shape
    (ih, iw) = img.shape
    out_h, out_w = ih, iw
    if fh > 1:
        out_h = ih - 2 * (fh // 2)
    if fw > 1:
        out_w = iw - 2 * (fw // 2)
    cc_img = np.zeros((out_h, out_w)).astype('float32')
    for x in range(ih - fh + 1):
        for y in range(iw - fw + 1):
            cc_img[x, y] = (filter * img[x: x + fh, y: y + fw]).sum()
    return cc_img


# Perform norm_cross_correlation on two image portions of same size
def norm_cross_correlation(filter, img):
    filter_energy = np.sqrt(np.square(filter).sum())
    img_energy = np.sqrt(np.square(img).sum())
    cc_img = (filter * img).sum()
    cc_img = cc_img / (filter_energy * img_energy)
    return cc_img

# Calculate the disparity across a row of the input images
def compute_row(x, imgL, imgR, window_size):
    print("## Start row: ", x)
    dims = len(imgL.shape)
    if dims == 3:
        (ih, iw, w) = imgL.shape
    else:
        (ih, iw) = imgL.shape
    fh = fw = window_size
    row_disp = []
    for y in range(iw - fw + 1):
        if dims == 3:
            window = imgL[x: x + fh, y: y + fw, :3]
        else:
            window = imgL[x: x + fh, y: y + fw]
        lst = []
        for z in range(iw - fw + 1):
            if dims == 3:
                cc_norm = norm_cross_correlation(window, imgR[x: x + fh, z: z + fw, :3])
            else:
                cc_norm = norm_cross_correlation(window, imgR[x: x + fh, z: z + fw])
            lst.append(cc_norm)
        lst = np.array(lst)
        row_disp.append(np.argmax(lst) - y)
    print("##-- End row: ", x)
    return row_disp

# Calculate the disparity by running compute_row function in parallel for diffrenet rows in the input image
def get_disparity_parallel(imgL, imgR, num_jobs=8, window_size=20):
    dims = len(imgL.shape)
    if dims == 3:
        (ih, iw, w) = imgL.shape
    else:
        (ih, iw) = imgL.shape
    fh = fw = window_size
    disparity = Parallel(n_jobs=num_jobs)(delayed(compute_row)(x, imgL, imgR, window_size) for x in range(ih - fh + 1))
    disparity = np.array(disparity)
    print("Shape of disparity: ", disparity.shape)
    return disparity

# Replacing the values of pixels that are at infinite depth
def replaceInf(depth):
    if math.isinf(np.unique(depth)[-1]):
        placeholder = np.unique(depth)[-2]
        for i in range(depth.shape[0]):
            for j in range(depth.shape[1]):
                if math.isinf(depth[i][j]):
                    depth[i][j] = placeholder
    return depth

# Calculate the disparity
def get_disparity(imgL, imgR, window_size=20):
    (ih, iw, w) = imgL.shape
    fh = fw = window_size
    out_h = ih - 2 * (fh // 2)
    out_w = iw - 2 * (fw // 2)
    off_set = fh // 2
    disparity = np.zeros((out_h, out_w)).astype('float32')
    for x in range(ih - fh + 1):
        for y in range(iw - fw + 1):
            window = imgL[x: x + fh, y: y + fw, :3]
            lst = []
            for z in range(iw - fw + 1):
                cc_norm = norm_cross_correlation(window, imgR[x: x + fh, z: z + fw, :3])
                lst.append(cc_norm)
            lst = np.array(lst)
            disparity[x][y] = np.argmax(lst) - y
    return disparity

# Read the calibration file to get focal length and baseline
def get_camera_calib(calib_loc):
    with open(calib_loc) as f:
        lines = f.readlines()
        focal = float(lines[0].split('=[')[1].split(' ')[0])
        baseline = float(lines[3].split('=')[1])
        return focal, baseline

# Calculating depth from disparity
def get_depth(disparity, focal_length, baseline ):
    z = (focal_length * baseline) / disparity
    z = replaceInf(z)
    return z


# Display 2 images, easier for comparisons
def displayTwoImages(left, right):
    imageL = cv2.cvtColor(left, cv2.COLOR_BGR2RGB)
    imageR = cv2.cvtColor(right, cv2.COLOR_BGR2RGB)

    f, ax = plt.subplots(1, 2)

    ax[0].imshow(imageL)
    ax[0].set_title("Left Image")
    ax[1].imshow(imageR)
    ax[1].set_title("Right Image")
    plt.show()