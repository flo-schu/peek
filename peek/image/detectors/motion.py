import cv2 as cv
from image.process import Image
from image.detectors.base import Detector, Mask, Tagger

class MotionDetector(Detector):
    class Trimmer(Mask):
        pass

    class MotionTagger(Tagger):
        def wrap_up(self):
            del self.properties
            del self.pois

    def tag_images(self, im1, im2, thresh_binary=15, thresh_size=10, mar=10):
        """
        motion analysis algorithm. First computes the difference between images.
        
        lag:            is the step between images which are differenced. Default is 1.
                        the higher the step the more pronounced the images should be. 
                        but consequently fewer images are available
        thresh_binary:  threshold to create a binary image from a gray image
        thresh_size:    after tag boxes have been drawn, choose select boxes
                        with maximum extension (x or y) of 'thresh_size'
        """
        tags = self.MotionTagger()
        diff = self.difference([im1, im2], lag=1)
        gray = cv.cvtColor(diff[0], cv.COLOR_BGR2GRAY)

        #threshold the gray image to binarise it. Anything pixel that has
        #value more than 3 we are converting to white
        #(remember 0 is black and 255 is absolute white)
        #the image is called binarised as any value less than 3 will be 0 and
        # all values equal to and more than 3 will be 255

        thresh = cv.threshold(gray, thresh_binary, 255, cv.THRESH_BINARY)
        cnts_select = self.get_contours(thresh[1], thresh_size)

        imtag = Image.tag_image(im2, cnts_select, mar)
        imslc1 = Image.cut_slices(im2, cnts_select, mar)
        imslc2 = Image.cut_slices(im2, cnts_select, mar)

        tags.tag_contour = cnts_select
        tags.tag_image_orig = imslc1
        tags.tag_image_diff = imslc2
        tags.wrap_up()

        return tags
