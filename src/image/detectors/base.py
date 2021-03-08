import cv2 as cv
import numpy as np
import imutils
import itertools as it
from matplotlib import pyplot as plt
from utils.manage import Files
from image.process import Series, Image
from image.analysis import Spectral

class Mask(Spectral):
    def __init__(self, img):
        self.img = img
        self.gray = np.array([])
        self.masks = {}
        self.pars = {}
 
    def create_masks(self, pars):
        """
        algorithm to create masks of different regions in the nanocosms
        The algorithm nows:
        - sediments (detection works very well)
        - blue band (works very well too)
        - airspace between blue band and water surface. Not yet ideal
        - water surface, also not working perfectly

        Mostly the subroutines work by homogenizing surfaces by applying a 
        sequence of a minimum filter of input image, from which a mask is 
        calculated from the a color channel which ideally it has a very distinct 
        transition from the regions which are to be spearated. Afterwards, color
        ranges are selected from the whole image or a specific channel. 
        Then a max filter is calculated from this to make the region 
        more homogeneous
        [ ] this could be improved by including other color channels as well
        [x] or converting to greyscale beforehand

        Then two methods are currently available:
        1. Extract vertical peaks from the image with scipy.signal
        2. Extract extrema in vertical spectral ranges with scipy.signal

        Both methods work by passing 1D vertical slices to the respective function
        to get extrema or peaks
        [ ] Maybe this could again be improved by finding the closest inflection
            point or peak to the previous, thus noisy (up and down moevements 
            would be avoided) !!!
        
        From the resulting line, a mask is extended until the bottom or another 
        line which contains the region of interest.
        
        The good thing with this, is that we are only slightly dependent on a color range 
        because this changes with lighting conditions or sediment cover, the important
        thing necessary is a big enough change. 

        In a nutshell
        1. MIN -> RANGE -> MAX
        2. PEAK/SIGNAL detection
        3. MASKING

        A further option would be to fit geometric shapes to regions like the 
        water surface. Becaus it will follow an ellipsis every time. It should
        be "relatively" easy to fit an ellipsis if there are several constraints.
        """

        if isinstance(pars, str):
            self.pars = Files.read_settings(pars)

        assert isinstance(self.pars, dict), "input parameters must be of type dict"



    @staticmethod
    def apply_mask(img, mask, action="remove"):
        if action == "remove":
            mask = mask == False
            mask = mask.astype('uint8')
        if action == "show":
            mask = mask
        
        return cv.bitwise_and(img, img, mask=mask)

    def remove_blue_tape(
        self, blue_low=[0,0,0], blue_high=[0,0,0], 
        min_kernel_n=0, max_kernel_n=255, apply_mask=True
        ):
        mask = self.mrm(
            self.img, 
            min_kernel_n=min_kernel_n, 
            range_threshold=(np.array(blue_low), np.array(blue_high)), 
            max_kernel_n=max_kernel_n)

        self.masks['blue_tape'] = self.mask_from_top(mask)

        if apply_mask:
            self.img = self.apply_mask(self.img, self.masks['blue_tape'])

    @staticmethod
    def trim(img, t=None, b=None, l=None, r=None):
        if t is None:
            t = 0
        if b is None:
            b = img.shape[0]
        if l is None:
            l = 0
        if r is None:
            r = img.shape[1]

        return img[t:b, l:r, :]

    def mask_sediment(self, y_offset=0, min_kernel_n=1, max_kernel_n=1,
                      gray_low=0, gray_high=255, peak_height=100, peak_width=50,
                      apply_mask=True):

        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        mask = self.mrm(
            gray[y_offset:], 
            min_kernel_n=min_kernel_n,
            range_threshold=(gray_low, gray_high),
            max_kernel_n=max_kernel_n)

        # detect peaks
        left, right = self.detect_vertical_peaks(mask, height=peak_height, 
                                                 width = peak_width)

        # redraw mask based on peak analysis
        # using np.zeros instead of np.ones with fill=1 instead of fill=0 
        # inverts the process
        newmask = self.extend_horiz_border(
            left, img=np.zeros(gray.shape), towards="bottom", 
            y_offset=(y_offset, y_offset), fill=1)

        self.masks['sediment'] = newmask
        
        if apply_mask:
            self.img = self.apply_mask(self.img, self.masks['sediment'])

    def mask_airspace(self, y_offset=0, min_kernel_n=1, max_kernel_n=1,
                      gray_low=0, gray_high=255, peak_height=100, peak_width=50,
                      apply_mask=True):

        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        mask = self.mrm(
            gray[:y_offset], 
            min_kernel_n=min_kernel_n,
            range_threshold=(gray_low, gray_high),
            max_kernel_n=max_kernel_n)

        # detect peaks
        left, right = self.detect_vertical_peaks(mask, height=peak_height, 
                                                 width=peak_width)

        newmask = self.extend_horiz_border(
            right, img=np.zeros(gray.shape), towards="top", 
            y_offset=(0, 0), fill=1)
        
        self.masks['airspace'] = newmask

        if apply_mask:
            self.img = self.apply_mask(self.img, self.masks['airspace'])

    def mask_water_surface(self, y_offset=0, color_channel=2, min_kernel_n=1,
                           max_kernel_n=1, color_low=0, color_high=255, 
                           smooth_n=0, apply_mask=True):
        # detect peaks
        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        mask = self.mrm(
            self.img[:y_offset,:,color_channel], 
            min_kernel_n=min_kernel_n,
            range_threshold=(color_low, color_high),
            max_kernel_n=max_kernel_n)
        left, right = self.detect_vertical_extrema(
            mask, 
            smooth_n=smooth_n, 
            derivative=1)
        newmask = self.extend_horiz_border(
            left, img=np.zeros(gray.shape), towards=right, 
            y_offset=(0, 0), fill=1, smooth_n=smooth_n)

        self.masks['water_surface'] = newmask

        if apply_mask:
            self.img = self.apply_mask(self.img, self.masks['water_surface'])


class Detector():

    @staticmethod
    def difference(images, lag=1, smooth=1):
        """
        calculates the RGB differences between every two consecutive images.
        The last difference is the diff between last and first image
        """
        # changing the dtype from uint to int is very important, because
        # uint does not allow values smaller 0
        kernel = np.ones((smooth,smooth),np.float32)/smooth**2
        images = np.array([cv.filter2D(i, -1, kernel) for i in images], dtype=int)
        # ims = np.array([i.img for i in imlist], dtype=int)
        diff = np.diff(images, n=lag, axis=0)
        diffs = np.where(diff >= 0, diff, 0)

        return [diffs[i,:,:,:].astype('uint8') for i in range(len(diffs))]        

    @staticmethod
    def get_contours(img, threshold):
        cnts = cv.findContours(img, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        cnts_select = []
        for c in cnts:
            # fit a bounding box to the contour
            if max(c.shape) > threshold:            
                cnts_select.append(c)

        return cnts_select

    @staticmethod
    def pass_tests(dict):
        return dict

    @staticmethod
    def get_contour_centers(contours):
        points = []
        for c in contours:
            box = cv.boundingRect(c)
            center = (box[0] + int(np.round(box[2]/2)), 
                      box[1] + int(np.round(box[3]/2)))
            points.append(center)
        
        return points

    @staticmethod
    def intersection(img, maxval=255):
        intersec = ( img[:,:,0] * img[:,:,1] 
                   + img[:,:,0] * img[:,:,2] 
                   + img[:,:,2] * img[:,:,1] )
        return np.where(intersec >= maxval, 255, 0).astype('uint8')

    @classmethod
    def find_pois(cls, im1, im2, filter_fun=None, filter_args={}, threshold=20, sw=20, 
                  erode_n=1, smooth=1, plot=False):
        diff = cls.difference([im1, im2], lag=1, smooth=3)[0]
        ret, thresh = cv.threshold(diff, threshold, 255,0)

        # get intersection of thresholded values
        intersec = cls.intersection(thresh, 1)

        # combine elements
        k = cv.getStructuringElement(cv.MORPH_ELLIPSE, ksize=(sw, sw))
        morph = cv.morphologyEx(intersec, op=cv.MORPH_CLOSE, kernel=k)

        # remove intersections of just 1 pixel (could maybe removed later)
        morph = Spectral.min_filter(erode_n, morph)
        contours, hierarchy = cv.findContours(morph, cv.RETR_TREE, 
                                              cv.CHAIN_APPROX_SIMPLE)

        if filter_fun is not None:
            contours = filter_fun(contours, **filter_args)

        points = cls.get_contour_centers(contours)

        if plot:
            fig, (ax1, ax2) = plt.subplots(1,2, sharey=True, sharex=True)
            ax1.imshow(im2)
            ax2.imshow(diff)

        return points

    @staticmethod
    def substract_median(img, ignore_value=None):
        im = img.copy().astype('int')
        assert len(img.shape) >= 2, "img must be 2D and have at least one color channel"

        if len(img.shape) == 2:
            im[:,:] = im[:,:] - np.median(im[:,:].flatten())
            
        elif len(img.shape) == 3:
            y, x, colors = img.shape

            for c in range(colors):
                data = im[:,:,c].flatten()
                if ignore_value is not None:
                    data = np.ma.masked_where(data == ignore_value, data).compressed()
                im[:,:,c] = im[:,:,c] - np.median(data)

        return np.where(im > 0, im, 0).astype('uint8')

    @staticmethod
    def get_roi(img, poi, search_width):
        im = img.copy()
        y, x, c = img.shape
        pt1 = tuple([max(p - search_width, 0) for p in poi])
        pt2 = tuple([min(poi[0] + search_width, x), min(poi[1] + search_width, y)])
        return im[pt1[1]:pt2[1], pt1[0]:pt2[0], :]

    @classmethod
    def detect(cls, img, poi, search_width, detector_fun, detector_args={}, plot=False ):
        # extract region of interest
        roi = cls.get_roi(img, poi, search_width)

        steps = detector_fun(roi, **detector_args)    
        
        if plot:
            nrow = int(np.ceil(np.sqrt(len(steps))))
            ncol = int(np.ceil(len(steps) / nrow))
            fig, axes = plt.subplots(nrow, ncol, sharex=True, sharey=True)
            for i, ax in enumerate(it.product(range(nrow), range(ncol))):
                try:
                    axes[ax[0], ax[1]].imshow(steps[i])
                except IndexError:
                    pass
                # axes[0,0].set_title("step 1: roi")

        return steps

    @staticmethod
    def unite_family(hierarchy, contours):
        if hierarchy is None:
            return []
        h = hierarchy.copy()[0]
        children = np.where(np.logical_and(h[:,2] == -1, h[:,3] != -1))[0].tolist()
        remove_childs = list()
        while len(children) > 0:
            parents = h[children,3].tolist()

            for p, c in zip(parents, children):
                contours[p] = np.row_stack((contours[p], contours[c]))

            h = np.delete(h, children, axis=0)
            remove_childs.extend(children)
            # children = np.where(h[:,2] == -1)[0].tolist()
            children = np.where(np.logical_and(h[:,2] == -1, h[:,3] != -1))[0].tolist()


        remove_childs.sort(reverse=True)
        for child in remove_childs:
            del contours[child]

        return contours

    @staticmethod
    def find_ellipses_in_contours(img, contours, draw=False):
        """
        only consider contours whose area can be determined. Otherwise they are
        of no use. The if else conditions can remain hardcoded, because they are the
        absolute minimal requirements for determining an ellipsis.
        """
        roi = img.copy() 
        center = np.array(Image.get_center_2D(roi))
        properties = []
        for i, c in enumerate(contours):
            m = cv.moments(c)
            
            if len(c) >= 5:
                props = {}
                e = cv.fitEllipse(c)
                props['id'] = i
                props['distance'] = np.linalg.norm(np.array(e[0]) - center) 
                props['area'] = m['m00'] 
                props['xcenter'] = e[0][0]
                props['ycenter'] = e[0][1]
                props['len_minor'] = e[1][0]
                props['len_major'] = e[1][1]
                props['angle'] = e[2]
                properties.append(props)
                
                if draw:
                    # for p in range(c.shape[0]):
                    #     roi = cls.draw_cross(
                    #         roi, c[p][0][0], c[p][0][1], 1, 
                    #         color=(0, 100,0))
                    roi = cv.ellipse(roi, e, (0,255,0), 1)
                    roi = Image.draw_cross(
                        roi, round(e[0][0]), round(e[0][1]), 1, 
                        color=(0,255,0))
            
            elif len(c) >= 4:
                if draw:
                    roi = cv.drawContours(roi, contours, i, (0,200,200), 1)
            
            elif m['m00'] == 0:
                if draw:
                    roi = cv.drawContours(roi, contours, i, (255,0,0), 1)

        return roi, properties, contours
        
    @staticmethod
    def select_and_sort(zipper, by):
        select = [(p[by], p, c) for p, c in zipper if p['select']]
        return [(p, c) for by, p, c in sorted(select)]
    
class Tagger():
    def __init__(self):
        self.tag_contour = []
        self.tag_image_orig = []
        self.tag_image_diff = []
        self.properties = []
        self.pois = []
    
    def add(self, tag, value):
        getattr(self, tag).append(value)

    def set_none(self, keys=[]):
        for k in keys:
            getattr(self, k).append(None)

    def move(self, search_width=50, manual=(0,0)):
        for i, (p, cont, prop) in enumerate(zip(self.pois, self.tag_contour, self.properties)):
            if cont is not None and prop is not None:
                self.tag_contour[i] = cont - search_width + p + manual
                try:
                    self.properties[i]['xcenter'] = prop['xcenter'] - search_width + p[0] + manual[0]
                    self.properties[i]['ycenter'] = prop['ycenter'] - search_width + p[1] + manual[1]
                except KeyError:
                    pass

    def show(self, img):
        cs = [c for c in self.tag_contour if c is not None]

        im = img.copy()
        im = Image.tag_image(im, cs)

        for p in self.pois:
            Image.draw_cross(im, p[0], p[1], 3, (255,0,0))

        plt.imshow(im)

    def update_props(self, key, val):
        if isinstance(val, list):
            assert len(val) == len(self.properties), "val should have the same length as properties"
        
        else:
            val = [val for i in range(len(self.properties))]

        for p, v in zip(self.properties, val):
            p[key] = v

    def drop(self, key):
        for p in self.properties:
            if key in p:
                del p[key]

    

