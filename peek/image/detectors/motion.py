import cv2 as cv
import numpy as np
import tqdm
from matplotlib import pyplot as plt
from skimage import measure
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
    ):
        # parent class has no attributes, make sure only attributes in 
        # class remain parameters
        self.margin = margin
        self.thresh_binary = thresh_binary
        self.thresh_size = thresh_size
        self.smooth = smooth
        self.max_clusters = max_clusters
        self.min_area = min_area

    def tag_images(self, batch):
        """
        motion analysis algorithm. First computes the difference between images.
        """
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
            cnts_select = self.get_contours(thresh, self.thresh_size)

            # update tags
            tags.tag_contour = cnts_select
            img_orig.tags = tags
            
            # add other images, which should be shown 
            img_orig.tag_image_comp = img_comp.pixels
            img_orig.tag_image_thresh = thresh

        return batch
    
    def slice_tags(self, batch):
        """
        optional method for creating sliced images of the tags. Good for 
        generating data for machine learning algorithm
        """
        mar = self.margin
        for img in batch.images:            

            # cut slices ALWAYS reusing the same contours

            # cut slices from the real image
            img.tags.tag_image_orig = img._cut_slices(img.pixels, mar, True)
            
            # cut slices from comparison image
            img.tags.tag_image_comp = img._cut_slices(img.tag_image_comp, mar, True)
            
            # cut slices from thresholded difference image
            img.tags.tag_image_thresh = img._cut_slices(img.tag_image_thresh, mar, True)

            # img.post_process_tags(
            #     pptag, 
            #     ["tag_image_thresh", "tag_image_orig", "tag_image_comp"]
            # )


        return batch


    def filter_tags(self, tags):
        # create new tag properties
        tags.new("n_clusters")
        tags.new("pixels_central")
        tags.new("axis_major_length")
        tags.new("axis_minor_length")

        thresh_slices = tags.tag_image_thresh

        remove_tags = []

        with tqdm.tqdm(total=len(thresh_slices)) as pbar:

            for i, thresh in enumerate(thresh_slices):
                # find clusters in threshold image with direct connectivity
                pbar.update(1)
                labels, n_cluster = measure.label(
                    thresh, return_num=True, connectivity=1)
                rp = measure.regionprops(labels)

                # get properties of central cluster
                central_label = labels[self.margin, self.margin]
                props = rp[central_label - 1]

                area_central_cluster = props.area
                # filter depending on labels
                if n_cluster > self.max_clusters:
                    remove_tags.append(i)
                    continue
                
                if area_central_cluster < self.min_area:
                    remove_tags.append(i)
                    continue

                # check out props. It has many attributes
                tags.add("n_clusters", n_cluster)
                tags.add("pixels_central", area_central_cluster)
                tags.add("axis_major_length", props.axis_major_length)
                tags.add("axis_minor_length", props.axis_minor_length)

        tags.filter_tags(properties=[
            "tag_contour", "tag_image_orig", "tag_image_thresh", "tag_image_comp"],
            drop_ids=remove_tags)

        return tags

def pptag(self, objs):
    fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize=(8,3))
    ax1.imshow(objs[0])
    ax2.imshow(objs[1])
    ax3.imshow(objs[2])


    fig.text(.1, .9, "")
    fig.savefig("work/temp/slice.png")
    plt.close()

    a = 2