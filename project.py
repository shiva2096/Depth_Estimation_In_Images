#!/usr/bin/env python
# coding: utf-8

import config
import numpy as np
import cv2
import matplotlib.pyplot as plt
import math
from utils import *

pathToImagesFolder = 'images/bike/'

# Read left and right image in greyscale
imLeft = cv2.imread(pathToImagesFolder + 'im0.png').astype('float32')
imRight = cv2.imread(pathToImagesFolder + 'im1.png').astype('float32')

# Read the focal length and baseline for the calibration file
focal_length, baseline = get_camera_calib(pathToImagesFolder + 'calib.txt')

# Resizing the images
imLeft = resizeImage(imLeft, 500)
imRight = resizeImage(imRight, 500)

# Display input images
displayTwoImages(imLeft.astype('uint8'), imRight.astype('uint8'))

# Calculate Disparity using the parallel function
disparity = get_disparity_parallel(imLeft, imRight, num_jobs=8, window_size=5)

# Calculating Depth
z = get_depth(disparity,focal_length, baseline)
z = normalizeImage(z)

# Display output images
displayImage(z.astype('uint8'))
displayImage(z.astype('uint8'), cm = 'prism')
displayImage(z.astype('uint8'), cm = 'flag')

