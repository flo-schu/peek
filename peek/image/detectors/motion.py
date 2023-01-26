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

        # create a list of the series length + 1, to get a difference image
        # from the 3rd and the 1st image
        pixel_imgs = batch.pixels + [batch.pixels[0]]
        difference_images = self.difference(pixel_imgs, smooth=smooth)

        #threshold the gray image to binarise it. Anything pixel that has
        #value more than 3 we are converting to white
        #(remember 0 is black and 255 is absolute white)
        #the image is called binarised as any value less than 3 will be 0 and
        # all values equal to and more than 3 will be 255

        zipper = zip(
            batch.images, 
            np.roll(difference_images, 1, axis=0)
        )
        for img, diff in zipper:
            tags = self.MotionTagger()
            # TODO: try if this is better placed before
            gray = cv.cvtColor(diff, cv.COLOR_BGR2GRAY)
            thresh = cv.threshold(gray, thresh_binary, 255, cv.THRESH_BINARY)
            cnts_select = self.get_contours(thresh[1], thresh_size)

            tags.tag_contour = cnts_select
            tags.wrap_up()
            img.tags = tags

        return batch
    
    def slice_tags(self, batch, mar=10):
        """
        optional method for creating sliced images of the tags. Good for 
        generating data for machine learning algorithm
        """
        for img_orig, img_diff_ in zip(batch.images, np.roll(batch.images, 1, axis=0)):
            
            # load the diff image again to avoid any mess-up
            img_diff = Snapshot(img_diff_.path)
            img_diff.tags = self.MotionTagger()

            # copy tag contours from original image
            img_diff.tags.tag_contour = img_orig.tags.tag_contour

            # cut out the same slices of tags from the two difference images
            img_orig.tags.tag_image_orig = img_orig.cut_slices(mar)
            img_orig.tags.tag_image_diff = img_diff.cut_slices(mar)

        return batch
