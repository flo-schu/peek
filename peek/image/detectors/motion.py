import cv2 as cv
import numpy as np
import copy
from peek.image.process import Snapshot
from peek.image.detectors.base import Detector, Mask, Tagger

class MotionDetector(Detector):
    class Trimmer(Mask):
        pass

    class MotionTagger(Tagger):
        def wrap_up(self):
            del self.properties
            del self.pois
            del self.tag_image_diff
            del self.tag_image_orig

    def tag_images(self, batch, thresh_binary=15, thresh_size=10, smooth=1):
        """
        motion analysis algorithm. First computes the difference between images.
        
        lag:            is the step between images which are differenced. Default is 1.
                        the higher the step the more pronounced the images should be. 
                        but consequently fewer images are available
        thresh_binary:  threshold to create a binary image from a gray image
        thresh_size:    after tag boxes have been drawn, choose select boxes
                        with maximum extension (x or y) of 'thresh_size'
        """


        comparison = zip(
            batch.images, 
            np.roll(batch.images, -1, axis=0),
        )
        for img_orig, img_comp in comparison:
            # calculate pixel and channel wise difference
            diff = self.difference(
                images=[img_comp.pixels, img_orig.pixels], 
                smooth=smooth)

            # TODO: try if this is better placed before
            # grayscale
            gray = cv.cvtColor(diff[0], cv.COLOR_BGR2GRAY)
            
            # threshold grayscale image
            _, thresh = cv.threshold(gray, thresh_binary, 255, cv.THRESH_BINARY)
            
            # get contours
            cnts_select = self.get_contours(thresh, thresh_size)

            # update tags
            tags = self.MotionTagger()
            tags.tag_contour = cnts_select
            tags.wrap_up()
            img_orig.tags = tags
            
            # add other images, which should be shown 
            img_orig.tag_image_diff = img_comp.pixels
            img_orig.tag_image_extra1 = thresh

        return batch
    
    def slice_tags(self, batch, mar=10):
        """
        optional method for creating sliced images of the tags. Good for 
        generating data for machine learning algorithm
        """
        for img in batch.images:            

            # cut slices ALWAYS reusing the same contours

            # cut slices from the real image
            img.tags.tag_image_orig = img.cut_slices(mar)
            
            # cut slices from comparison image
            img.tags.tag_image_diff = img._cut_slices(img.tag_image_diff, mar)
            
            # cut slices from thresholded difference image
            img.tags.tag_image_extra1 = img._cut_slices(img.tag_image_extra1, mar)

        return batch
