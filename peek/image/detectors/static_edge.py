import cv2 as cv
import numpy as np
from image.process import Image 
from image.detectors.base import Detector, Mask, Tagger
from progress.bar import IncrementalBar
from matplotlib import pyplot as plt
# import gc

# here I can create my own individual program of functions, that I want to execute
# This is very nice, because here it makes it explicit what is to be done,
# but leaves the overhead out of the way


class StaticEdgeDetector(Detector):
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
        def wrap_up(self, trim_top):
            self.update_props("xpoi", [px+0 for px, py in self.pois])
            self.update_props("ypoi", [py+trim_top for px, py in self.pois])
            del self.pois
            del self._nitems
            del self.tag_image_diff


    @staticmethod
    def filter_contours(contours, ratio_gt=None, area_gt=10000):
        delete_keys = []
        for key, c in contours.items():
            if cv.moments(c['contour'])['m01'] / max(1, cv.moments(c['contour'])['m10']) > 100:
                # filters contours with a very off width to length ratio
                delete_keys.append(key)
            
            if cv.moments(c['contour'])["m00"] > 2000:
                delete_keys.append(key)
            
        for k in delete_keys:
            del contours[k]

        return contours

    def tag_image(self, img, 
                  mask_config,
                  preprocess_config,
                  filter_config,
                  progress_bar=False,
                  show_plots=False):
        
        # initialize Tagger
        tags = self.DetectSelectSortTagger()

        # mask images
        m = self.mask_image(img, masker=self.Slice, parfile=mask_config, mask=None)
        # m2 = self.mask_images(img2, parfile, mask=m)

        impp = self.preprocess(m.img, 
            algorithm=preprocess_config["algorithm"], 
            algorithm_kwargs=preprocess_config["parameters"])

        pois, contours = self.generate_pois(impp[-1], 
            filter_fun=self.filter_contours, 
            filter_args=filter_config)

        if show_plots:
            impp.append(Image.tag_image(impp[1], contours))
            self.plot_grid(impp)


        for poi, cnt in zip(pois, contours):
            # rescale and slice
            cnt = tags.rescale(cnt, impp[0], impp[1])
            poi = tags.rescale(poi, impp[0], impp[1])
            slc = Image.slice_image(impp[0], *cv.boundingRect(cnt))

            tags.add("pois", poi)
            tags.add("tag_contour", cnt)
            tags.add("tag_image_orig", slc)
            tags.tick()

        tags.wrap_up(trim_top=m.pars['trim']['t'])
        return tags


# improvements:
# - use the same mask once created to avoid detection of changes,
#   just because of mask issues. Also saves processing power



# improvements:
# - use the same mask once created to avoid detection of changes,
#   just because of mask issues. Also saves processing power

# finish:
# - create tags:
#   1. add contour, image and x, y of center to tags
#   2. scale everything because of resizing
#   3. thats it.
# - future work:
#   write method to join overlapping contour regions.