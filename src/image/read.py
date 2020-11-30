import rawpy
import imageio
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# preprocessing script adaptedfrom Kaarina 
path = "../../data/pics/20201112/Serienbilder013/"
pic = "P1000086.RW2"

def crop_image(path,pic):
    assert os.path.isfile(path+pic)
    with rawpy.imread(path+pic) as raw:
        rgb = raw.postprocess()

    imageio.imsave(path+"temp.tiff", rgb)
    img = cv2.imread(path+"temp.tiff")

    # crop top and bottom, to increase speed
    cimg = img[1000:4000, :,:]

    # calculate sum of rgb colors (black is zero)
    bwimg = cimg.sum(axis=2)

    # find minimum of vertical pixel columns 
    black = bwimg.min(axis=0)

    # take cumulative sum of BW values in each column
    # to find the longest continuous row of black.
    # This is where is to be cut off
    cutl = black.cumsum() != 0
    cutr = black[::-1].cumsum()[::-1] != 0

    # if needed, the value progression of BW can be plotted
    # plt.plot(bwimg[-100,:])

    # take subset of cuts from left and right
    ccimg = cimg[:, np.logical_and(cutl,cutr),:]

    # save image as tiff and delete temp
    os.remove(path+"temp.tiff")
    cv2.imwrite(path+"cropped2.tiff", ccimg)

crop_image(path, pic)

pics = ["P1000086.RW2","P1000089.RW2"]

def difference_img(path, pics)
    for p in pics:
        assert os.path.isfile(path+p)
    
    rgbs = []
    for p in pics:
        with rawpy.imread(path+p) as raw:
            rgbs.append(raw.postprocess())
    

    arr = np.array(rgbs)
    arr[:,5000,500,0]
    test = rgbs[0]+ rgbs[1]*-1
    
    cv2.imwrite(path+"diff.tiff", test)

    # works like a charm :)
    # to generate labelled data, I can make slices of the 
    # image and label the organisms with an easy program

    test

