import cv2 as cv
import numpy as np
import tqdm
from matplotlib import pyplot as plt
from skimage import measure
from peek.image.process import idstring_to_threshold_image, threshold_imgage_to_idstring
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

            # calculate pixel and channel wise difference
            diff = self.difference(
                images=[img_comp.pixels, img_orig.pixels], 
                smooth=self.smooth)

            # TODO: try if this is better placed before
            # grayscale
            gray = cv.cvtColor(diff[0], cv.COLOR_BGR2GRAY)

            # threshold grayscale image
            _, thresh = cv.threshold(gray, self.thresh_binary, 255, cv.THRESH_BINARY)
            
            # get contours
            img_orig.contours = self.get_contours(thresh, self.thresh_size)
            thresh_slices = img_orig._cut_slices(
                thresh, mar=self.margin, max_from_center=True)

            # update tags
            tags.tag_box_thresh_ids = [
                threshold_imgage_to_idstring(t) for t in thresh_slices]

            # get contour coordinates
            [tags.get_tag_box_coordinates(c, self.margin) for c in img_orig.contours]
            img_orig.tags = tags

            # add other images, which should be shown 
            img_orig.comparison = img_comp.pixels

        return batch
    
    # def slice_tags(self, batch):
    #     """
    #     optional method for creating sliced images of the tags. Good for 
    #     generating data for machine learning algorithm
    #     """
    #     mar = self.margin
    #     for img in batch.images:            

    #         # cut slices ALWAYS reusing the same contours

    #         # cut slices from the real image
    #         img.tags.tag_image_orig = img._cut_slices(img.pixels, mar, True)
            
    #         # cut slices from comparison image
    #         img.tags.tag_image_comp = img._cut_slices(img.tag_image_comp, mar, True)
            
    #         # cut slices from thresholded difference image
    #         img.tags.tag_image_thresh = img._cut_slices(img.tag_image_thresh, mar, True)

    #         # img.post_process_tags(
    #         #     pptag, 
    #         #     ["tag_image_thresh", "tag_image_orig", "tag_image_comp"]
    #         # )


    #     return batch


    def analyze_tags(self, tags):

        with tqdm.tqdm(total=tags.max_len, desc="analyzing") as pbar:

            for i in range(tags.max_len):
                # find clusters in threshold image with direct connectivity
                tag_props = self.analyse_tag(tags, i)

                # add props to tags
                _ = [tags.add(key, value) for key, value in tag_props.items()]

                pbar.update(1)
                
        assert tags.is_equal_properties_lengths()

        return tags

    def filter_tags(self, tags):
        drop_tags = []
        kept_tags = []
        with tqdm.tqdm(total=tags.max_len, desc="filtering") as pbar:

            for i in range(tags.max_len):
                keep = self.test_tag(tags, i)
                
                if keep:
                    kept_tags.append(i)
                else:
                    drop_tags.append(i)

                pbar.update(1)
            
        # tags.drop_tags(
        #     properties=list(tags.__dict__.keys()), 
        #     drop_ids=drop_tags
        # )
        assert tags.is_equal_properties_lengths()

        return kept_tags

    def analyse_tag(self, tags, i):
        thresh = tags.get("tag_box_thresh_ids", i)
        thresh = idstring_to_threshold_image(thresh, self.margin)
        labels, n_cluster = measure.label(
            thresh, return_num=True, connectivity=1)
        rp = measure.regionprops(labels)

        # get properties of central cluster
        central_label = labels[self.margin, self.margin]
        props = rp[central_label - 1]

        area_central_cluster = props.area

        tag_props = {
            "n_clusters": n_cluster,
            "pixels_central": area_central_cluster,
            "axis_major_length": props.axis_major_length,
            "axis_minor_length": props.axis_minor_length,
        }

        return tag_props

    def test_tag(self, tags, i):
        keep = True

        # apply test depending on labels
        if tags.get("n_clusters", i) > self.max_clusters:
            keep = False
        
        if tags.get("pixels_central", i) < self.min_area:
            keep = False

        x = tags.get("x", i)
        if x > self.max_x:
            keep = False

        if x < self.min_x:
            keep = False

        return keep

def pptag(self, objs):
    fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize=(8,3))
    ax1.imshow(objs[0])
    ax2.imshow(objs[1])
    ax3.imshow(objs[2])


    fig.text(.1, .9, "")
    fig.savefig("work/temp/slice.png")
    plt.close()

    a = 2