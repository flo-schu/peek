import cv2 as cv
import numpy as np
from image.detectors.base import Detector, Mask, Tagger
# from progress.bar import IncrementalBar
# import gc

# here I can create my own individual program of functions, that I want to execute
# This is very nice, because here it makes it explicit what is to be done,
# but leaves the overhead out of the way


class MovementEdgeDetector(Detector):
    class Slice(Mask):
        def create_masks(self, pars):
            super().create_masks(pars)

            self.img = self.trim(self.img, **self.pars['trim'])
            self.remove_blue_tape(**self.pars['blue_tape'])
            self.mask_sediment(**self.pars['sediment'])     
            # self.mask_airspace(**self.pars['airspace'])        
            # self.mask_water_surface(**self.pars['water_surface'])
            
        def apply_multi(self, masks):
            for m in masks.values():
                self.img = self.apply_mask(self.img, m)

    class DetectSelectSortTagger(Tagger):
        def wrap_up(self, search_radius, trim_top):
            self.move(search_width=search_radius, manual=(0, trim_top))
            self.update_props("xpoi", [px+0 for px, py in self.pois])
            self.update_props("ypoi", [py+trim_top for px, py in self.pois])
            self.update_props("search_radius", search_radius)
            self.drop('id')
            self.drop('select')
            del self.pois


    @staticmethod
    def filter_contours(contours):
        cnts = []
        for c in contours:
            if cv.moments(c)['m01'] / max(1, cv.moments(c)['m10']) > 100:
                pass
            else:
                cnts.append(c)

        return cnts

    @staticmethod
    def median_threshold(roi, blur, thresh):
        median = cv.medianBlur(roi, blur)
        background = Detector.substract_median(median, ignore_value=0)
        gray = cv.cvtColor(background, cv.COLOR_RGB2GRAY)
        T, thresh = cv.threshold(gray, thresh, 255, 0)
        return [roi, thresh]

    @staticmethod
    def pass_tests(d):
        d['select'] = True
        d['select'] = d['select'] and not d['len_major'] > 500
        d['select'] = d['select'] and not d['len_minor'] > 500
        d['select'] = d['select'] and not d['area'] < 5
        d['select'] = d['select'] and not d['area'] > 5000
        d['select'] = d['select'] and not (d['distance'] > 20 and d['area'] < 50)
        d['select'] = d['select'] and not (d['angle'] > 85 and d['angle'] < 95 and d['len_major'] > 90)
        return d

    def mask_images(self, im1, im2, parfile):
        # mask images
        m1 = self.Slice(im1)
        m1.create_masks(pars=parfile)

        m2 = self.Slice(im1)
        m2.img = m2.trim(im2, **m1.pars['trim'])
        m2.apply_multi(masks=m1.masks)

        return m1, m2

    def tag_image(self, im1, im2, dect_args, parfile,
                  search_radius, crit_multiple='distance'):
        
        # initialize Tagger
        tags = self.DetectSelectSortTagger()

        # mask images
        m1, m2 = self.mask_images()

        # from matplotlib import pyplot as plt

        # determin points of interest
        pois = self.find_pois(
            m2.img, m1.img, filter_fun=self.filter_contours, 
            threshold=20, sw=20, erode_n=3)

        # main loop
        # bar = IncrementalBar('Processing', max=len(pois))
        for poi in pois:
            steps = Detector.detect(
                m1.img, poi, search_radius, 
                self.median_threshold, dect_args, plot=False
                )

            contours, hierarchy = cv.findContours(steps[-1], cv.RETR_TREE, 
                                                  cv.CHAIN_APPROX_NONE)
            
            contours = self.unite_family(hierarchy, contours)
            roi, properties, contours = self.find_ellipses_in_contours(
                steps[0], contours, draw=False
                )
            
            for p in properties:
                p = self.pass_tests(p)

            select = self.select_and_sort(zip(properties, contours), 
                                            by='distance')

            try:
                properties = select[0][0]
                contours = select[0][1]
            except IndexError:
                contours = np.empty((0,1,2), dtype=int)
                properties = {}
            
            tags.add("pois", poi)
            tags.add("properties", properties)
            tags.add("tag_contour", contours)
            tags.add("tag_image_orig", steps[0])
            tags.add("tag_image_diff", Detector.get_roi(m2.img, poi, search_radius))

            # gc.collect()
            # bar.next()

        # wrap up
        tags.wrap_up(search_radius, trim_top=m1.pars['trim']['t'])
        # bar.finish()

        return tags


# improvements:
# - use the same mask once created to avoid detection of changes,
#   just because of mask issues. Also saves processing power