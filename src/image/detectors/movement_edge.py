import cv2 as cv
import numpy as np
from image.detectors.base import Detector, Mask, Tagger

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
        return [roi, median, background, gray, thresh]

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

    class DetectSelectSortTagger(Tagger):
        def tag_image(self, mask_img1, mask_img2, pois, dect_fct, dect_args, 
                      test_fct, search_radius, crit_multiple='distance'):
            # main loop
            for poi in pois:
                steps = Detector.detect(mask_img1.img, poi, search_radius, dect_fct, 
                                        dect_args, plot=False)
                contours, hierarchy = cv.findContours(steps[-1], cv.RETR_TREE, 
                                                    cv.CHAIN_APPROX_NONE)
                contours = Detector.unite_family(hierarchy, contours)
                roi, properties, contours = Detector.find_ellipses_in_contours(
                    steps[0], contours, draw=False
                    )
                
                for p in properties:
                    p = test_fct(p)

                select = Detector.select_and_sort(zip(properties, contours), 
                                                by='distance')

                try:
                    properties = select[0][0]
                    contours = select[0][1]
                except IndexError:
                    contours = np.empty((0,1,2), dtype=int)
                    properties = {}
                
                self.add("pois", poi)
                self.add("properties", properties)
                self.add("tag_contour", contours)
                self.add("tag_image_orig", steps[0])
                self.add("tag_image_diff", Detector.get_roi(mask_img2.img, poi, search_radius))

            # wrap up
            self.move(search_width=search_radius, manual=(0, mask_img1.pars['trim']['t']))
            self.update_props("xpoi", [px+0 for px, py in self.pois])
            self.update_props("ypoi", [py+mask_img1.pars['trim']['t'] for px, py in self.pois])
            self.update_props("search_radius", search_radius)
            self.drop('id')
            self.drop('select')
            del self.pois
