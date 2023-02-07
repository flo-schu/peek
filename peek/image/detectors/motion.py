import cv2 as cv
import numpy as np
from skimage import measure
from peek.image.process import idstring_to_threshold_image, threshold_imgage_to_idstring, margin_to_shape
from peek.image.detectors.base import Detector, Tagger
from peek.image.analysis import Tag, Spectral

class MotionTagger(Tagger):
    # set extra standard attributes
    def __init__(self):
        super().__init__()
        self.img_comp_path = []

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
        thresh_bg=1, 
        thresh_size=1, 
        smooth=1,
        max_clusters=np.inf,
        min_area=1,
        max_x=np.inf,
        min_x=0,
        connectivity=1,
    ):
        # parent class has no attributes, make sure only attributes in 
        # class remain parameters
        self.margin = margin
        self.thresh_binary = thresh_binary
        self.thresh_bg = thresh_bg
        self.thresh_size = thresh_size
        self.smooth = smooth
        self.max_clusters = max_clusters
        self.min_area = min_area
        self.max_x = max_x
        self.min_x = min_x
        self.connectivity = connectivity

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
            tags = MotionTagger()
            
            thresh = self.multi_background_thresholding(
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
            
            tags.img_path = [img_orig.path] * tags.max_len
            tags.img_comp_path = [img_comp.path] * tags.max_len
            img_orig.tags = tags

            # add other images, which should be shown 
            img_orig.comparison = img_comp.pixels

        return batch


    def multi_background_thresholding(self, img_orig, img_comp):
        diff_for = self.difference(
            images=[img_comp, img_orig], 
            smooth=self.smooth)[0]
        
        diff_dup = self.difference(
            images=[img_orig, img_comp], 
            smooth=self.smooth, duplicates=True)[0]
        
        diff_gray_for = cv.cvtColor(diff_for, cv.COLOR_BGR2GRAY)
        diff_gray_dup = cv.cvtColor(diff_dup, cv.COLOR_BGR2GRAY)
                
        bg = cv.medianBlur(img_orig, 51)
        bggray = cv.cvtColor(bg, cv.COLOR_BGR2GRAY)
        _, bg_mask = cv.threshold(bggray, self.thresh_bg, 1, type=cv.THRESH_BINARY)
        
        diff = np.where(bg_mask, diff_gray_dup, diff_gray_for)
        _, thresh = cv.threshold(diff, self.thresh_binary, 255, type=cv.THRESH_BINARY)

        return thresh


    def thresholding(self, img_orig, img_comp):

        # img_orig_ = Spectral.max_filter(3, img=img_orig)
        # img_comp_ = Spectral.max_filter(3, img=img_comp)

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

    def analyze_tag(self, tag, neighbor=None):
        thresh = tag["tag_box_thresh_ids"]
        w, h = tag["width"], tag["height"]
        thresh = idstring_to_threshold_image(thresh, shape=(h, w))
        labels, n_cluster = measure.label(
            thresh, return_num=True, connectivity=self.connectivity)
        rp = measure.regionprops(labels)

        # get properties of central cluster
        central_label = labels[self.margin, self.margin]

        iou = self.get_iou(tag, neighbor[1])
        
        if len(rp) == 0:
            area_central_cluster = 0
            amal = 0
            amil = 0
            r, g, b = (0, 0, 0)
            rb, gb, bb = (0, 0, 0)
            contrast = 0

        else:
            mask = labels == central_label
            mask_color = np.tile(mask.reshape((*mask.shape, 1)), 3)
            # calculate properties based on the tag box of the orginal image
            tag_ = Tag(props=tag)
            original_slice = tag_.orig_img
            
            
            # contrast
            # calculate contrast by taking the difference to the comparison
            compare_slice = tag_.comp_img
            ogray = cv.cvtColor(original_slice, cv.COLOR_BGR2GRAY)
            cgray = cv.cvtColor(compare_slice, cv.COLOR_BGR2GRAY)
            diff = ogray.astype(int) - cgray.astype(int)
            masked_diff = np.ma.MaskedArray(diff, mask)

            # positive values mean bright on dark detection
            # negative values mean dark on bright detection
            # large values mean high contrast low values mean low contrast
            contrast = masked_diff.mean() 

            masked_slice = np.ma.MaskedArray(original_slice, mask_color)

            # get median colors of central cluster of original image
            r, g, b = np.ma.median(masked_slice, axis=(0,1))
            rb, gb, bb = np.ma.median(~masked_slice, axis=(0,1))

            props = rp[central_label - 1]
            area_central_cluster = props.area
            amal = props.axis_major_length
            amil = props.axis_minor_length
        
        tag_props = {
            "n_clusters": n_cluster,
            "pixels_central": area_central_cluster,
            "axis_major_length": amal,
            "axis_minor_length": amil,
            "red_cluster": r,
            "green_cluster": g,
            "blue_cluster": b,
            "red_background": rb,
            "green_background": gb,
            "blue_background": bb,
            "closest_neighbor": neighbor[0],
            "neighbor_iou": iou,
            "contrast": contrast,
        }

        return tag_props

    def test_tag(self, tag):
        keep = True

        if tag["pred"] == "duplicate":
            keep = False

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

