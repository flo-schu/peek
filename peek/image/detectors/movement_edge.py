import cv2 as cv
import numpy as np
import gc
import tqdm

from peek.image.process import Image
from peek.image.analysis import Preprocessing
from peek.image.detectors.base import Detector, Mask, Tagger

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
    def pass_tests(d):
        d['select'] = True
        d['select'] = d['select'] and not d['len_major'] > 500
        d['select'] = d['select'] and not d['len_minor'] > 500
        d['select'] = d['select'] and not d['area'] < 5
        d['select'] = d['select'] and not d['area'] > 5000
        d['select'] = d['select'] and not (d['distance'] > 20 and d['area'] < 50)
        d['select'] = d['select'] and not (d['angle'] > 85 and d['angle'] < 95 and d['len_major'] > 90)
        return d


    def tag_image(self, im1, im2, 
                  mask_config,
                  diff_config,
                  preprocess_config,
                  filter_config,
                  detector_config, 
                  progress_bar=False,
                  show_plots=False):
        
        # initialize Tagger
        tags = self.DetectSelectSortTagger()

        # mask images
        m1 = self.Slice(im1)
        m1.create_masks(pars=mask_config)
        m2 = self.Slice(im1)
        m2.img = m2.trim(im2, **m1.pars['trim'])
        m2.apply_multi(masks=m1.masks)

        # create diff image 
        diff = self.difference(
            [m2.img, m1.img], **diff_config)[0]        

        impp = self.preprocess(diff, 
            algorithm=preprocess_config["algorithm"], 
            algorithm_kwargs=preprocess_config["parameters"])

        # determin points of interest from diff
        pois, contours = self.find_pois(impp[-1], 
            filter_fun=self.filter_contours, 
            filter_args=filter_config)

        if show_plots:
            impp.append(Image.tag_image(impp[0], contours))
            self.plot_grid(impp)

        if progress_bar:
            with tqdm.tqdm(total=len(pois)) as bar:
                
                for poi in pois:
                    roi = self.get_roi(m1.img, poi, search_width=detector_config["search_radius"])
                    steps = Detector.preprocess(roi,
                        algorithm=detector_config["algorithm"], 
                        algorithm_kwargs=detector_config["parameters"])

                    contours, hierarchy = cv.findContours(steps[-1], cv.RETR_TREE, 
                                                        cv.CHAIN_APPROX_NONE)
                    
                    contours = self.unite_family(hierarchy, list(contours))
                    roi, properties, contours = self.find_ellipses_in_contours(
                        steps[0], contours, draw=False)
                    
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
                    gc.collect()
                    roi_diff = Detector.get_roi(m2.img, poi, search_width=detector_config["search_radius"])
                    tags.add("tag_image_diff", roi_diff)

                    gc.collect()
                    if progress_bar:
                        bar.update(1)

        # wrap up
        tags.wrap_up(search_radius=detector_config["search_radius"], 
                     trim_top=m1.pars['trim']['t'])

        return tags


# improvements:
# - use the same mask once created to avoid detection of changes,
#   just because of mask issues. Also saves processing power
