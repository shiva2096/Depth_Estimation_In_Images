# CV_GroupProject

Make your own branch and then merge at last and not on master.

Preprocessing steps:
1) Load images in grayscale and reshape it to 500*500.
2) Make it to float.
3) Filter out the noise using gaussian and see if it gives better results.

Prop1 =>
**Submit by 28th**
Do all these calulations in floating points. 
1) Pick all patches of (3*3) => (xL) from first image and see its max normalized cross-correlation on the parallel horizontal line in the second image => xR.
2) Once found, compute d = (xR - xL) OR called disparity.
3) After that compute depth using focal length. Formula z = (f*B)/d  where B is baseline and d is the disparity. iF have time make it (d+doff) for better results.
4) Scale this depth from float => 0-1 or or int => 0-255. If want to do viz => use cmap in plotlib.

**If we have time => **

Prop2 => 
1) Explore camera calib.
2) Do epipolar lines which are not horizontal(slanted lines).



Camera config => 
cam0=[3997.684 0 1176.728; 0 3997.684 1011.728; 0 0 1]
cam1=[3997.684 0 1307.839; 0 3997.684 1011.728; 0 0 1]
doffs=131.111
baseline=193.001
width=2964
height=1988
ndisp=280
isint=0
vmin=31
vmax=257
dyavg=0.918
dymax=1.516


Semantics of above terms => 

cam0,1:        camera matrices for the rectified views, in the form [f 0 cx; 0 f cy; 0 0 1], where
  f:           focal length in pixels
  cx, cy:      principal point  (note that cx differs between view 0 and 1)

doffs:         x-difference of principal points, doffs = cx1 - cx0

baseline:      camera baseline in mm

width, height: image size

ndisp:         a conservative bound on the number of disparity levels;
               the stereo algorithm MAY utilize this bound and search from d = 0 .. ndisp-1

isint:         whether the GT disparites only have integer precision (true for the older datasets;
               in this case submitted floating-point disparities are rounded to ints before evaluating)

vmin, vmax:    a tight bound on minimum and maximum disparities, used for color visualization;
               the stereo algorithm MAY NOT utilize this information

dyavg, dymax:  average and maximum absolute y-disparities, providing an indication of
               the calibration error present in the imperfect datasets.
               
               
Resource => https://vision.middlebury.edu/stereo/data/scenes2014/
