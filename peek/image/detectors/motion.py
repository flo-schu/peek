import cv2 as cv
import numpy as np
import tqdm
from matplotlib import pyplot as plt
from skimage import measure
from peek.image.process import idstring_to_threshold_image, threshold_imgage_to_idstring, margin_to_shape
from peek.image.detectors.base import Detector, Tagger

class MotionDetector(Detector):
    """
    margin          margin to created around the contours center for tag images        
    thresh_binary   threshold to create a binary image from a gray image
    thresh_size     after tag boxes have been drawn, choose select boxes
                    with maximum extension (x or y) of 'thresh_size'
    smooth          width of smoothing kernel
    max_clusters    max amount of connected pixel-clusters per tag
    min_area        minimum area (in pixels) of central cluster in tag
    """
    def __init__(
        self, 
        margin=10,
        thresh_binary=1, 
        thresh_size=1, 
        smooth=1,
        max_clusters=np.inf,
        min_area=1,
        max_x=np.inf,
        min_x=0
    ):
        # parent class has no attributes, make sure only attributes in 
        # class remain parameters
        self.margin = margin
        self.thresh_binary = thresh_binary
        self.thresh_size = thresh_size
        self.smooth = smooth
        self.max_clusters = max_clusters
        self.min_area = min_area
        self.max_x = max_x
        self.min_x = min_x

    def tag_images(self, batch):
        """
        motion analysis algorithm. First computes the difference between images.
        """
        print("\n generating difference images series. Always the difference with the next image is taken. The last image is compared with the first image.")

        comparison = zip(
            batch.images, 
            np.roll(batch.images, -1, axis=0),
        )
        for img_orig, img_comp in comparison:
            tags = Tagger()
            
            thresh = self.thresholding(
                img_orig=img_orig.pixels, 
                img_comp=img_comp.pixels
            )
            # get contours
            img_orig.contours = self.get_contours(thresh, self.thresh_size)
            thresh_slices = img_orig._cut_slices(
                thresh, mar=self.margin, max_from_center=True)

            # update tags
            tags.tag_box_thresh_ids = [
                threshold_imgage_to_idstring(t) for t in thresh_slices]

            # get contour coordinates
            [tags.get_tag_box_coordinates(c, margin_to_shape(self.margin)) 
                for c in img_orig.contours]
            img_orig.tags = tags

            # add other images, which should be shown 
            img_orig.comparison = img_comp.pixels

        return batch


    def thresholding(self, img_orig, img_comp):
        # calculate pixel and channel wise difference
        diff = self.difference(
            images=[img_comp, img_orig], 
            smooth=self.smooth)

        # TODO: try if this is better placed before
        # grayscale
        
        gray = cv.cvtColor(diff[0], cv.COLOR_BGR2GRAY)

        # threshold grayscale image
        _, thresh = cv.threshold(gray, self.thresh_binary, 255, cv.THRESH_BINARY)

        return thresh

    def analyze_tag(self, tag):
        thresh = tag["tag_box_thresh_ids"]
        w, h = tag["width"], tag["height"]
        thresh = idstring_to_threshold_image(thresh, shape=(h, w))
        labels, n_cluster = measure.label(
            thresh, return_num=True, connectivity=1)
        rp = measure.regionprops(labels)

        # get properties of central cluster
        central_label = labels[self.margin, self.margin]
        
        if len(rp) == 0:
            area_central_cluster = 0
            amal = 0
            amil = 0

        else:
            props = rp[central_label - 1]
            area_central_cluster = props.area
            amal = props.axis_major_length
            amil = props.axis_minor_length
        
        tag_props = {
            "n_clusters": n_cluster,
            "pixels_central": area_central_cluster,
            "axis_major_length": amal,
            "axis_minor_length": amil,
        }

        return tag_props

    def test_tag(self, tag):
        keep = True

        # apply test depending on labels
        if tag["n_clusters"] > self.max_clusters:
            keep = False
        
        if tag["pixels_central"] < self.min_area:
            keep = False

        x = tag["x"]
        if x > self.max_x:
            keep = False

        if x < self.min_x:
            keep = False

        return keep

