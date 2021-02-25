# ======= motion analysis to build a database for object detection ============
# this would be a task for a hyperparameter optimization ()

import os
from image.process import Series, Image
from image.analysis import Mask
from utils.manage import Files
from matplotlib import pyplot as plt

path = "../data/pics/"
date = "20210204"
copy_to = "../data/annotations/"
stop_after=100

s = Series(os.path.join(path, date, "7"))

# img = Image(os.path.join(path, date, "8", "091155"))
# img = Image(os.path.join(path, date, "6", "090953"))
img = Image(os.path.join(path, date, "7", "091355"))

masks = Mask(img.img)
masks.create_masks(pars="../settings/masking_20210225.json")
plt.imshow(masks.img)



# masks.img = masks.trim(masks.img,1000, 4500)
# masks.remove_blue_tape(**pars["blue_tape"])
# # plt.imshow(masks.apply_mask("blue_tape"))
# masks.img = masks.apply_mask("blue_tape")
# masks.mask_sediment(**pars["sediment"])
# # plt.imshow(masks.apply_mask("sediment"))
# masks.mask_airspace(**pars["airspace"])
# plt.imshow(masks.apply_mask("airspace"))


# remove from end of blue band to top ------------------------------------------
# 2. apply mask till blue band is detected



# remove sediment --------------------------------------------------------------
# create prelimary mask of sediment 


# remove distance to water surface ---------------------------------------------

# can the problems be resolved by fitting a cubic function through the points?
# because normally the correct points are identified


# plt.plot(gaussian_filter1d(right,100)); plt.plot(gaussian_filter1d(left,100))
# len(left)



# 3. apply mask until sediment is over
# minimum filters are used for this, because when the 
# radius is big enough, floating objects in water are "overwritten" with
# background. since sediment is continuously coloured, minimum of color 
# ranges is much higher here.

# to detect the sediment border, the picture is split in half, because in the
# lower half the sediment will start eventually.
# the input is a minimum filter of input image, from which a mask is calculated
# from the red channel because it has a very distinct transition from background 
# to sediment. Then a max filter is calculated from this to make the sediment 
# more homogeneous
# [ ] this could be improved by including other color channels as well
# [ ] or converting to greyscale beforehand

# Next, vertical 1D slices are passed to np.gradient two times to get
# the locations of the inflection points. The first one, marks the transition to 
# the sediment. 
# [ ] Maybe this could again be improved by finding the closest inflection
#     point to the previous, thus noisy (up and down moevements would be avoided)
#     !!!
# From the resulting line, a mask is extended until the bottom and contains the
# sediment.
# The good thing with this, is that we are only slightly dependent on a color range 
# because this changes with lighting conditions or sediment cover, the important
# thing necessary is a big enough change. 

# next time try out:
# 1. Greyscale
# 2. min filter --> mask --> max filter
# 3. detect change
# 4. find beginning and then advance by closest location

