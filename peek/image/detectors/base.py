import os
import warnings
import cv2 as cv
import numpy as np
import imutils
import itertools as it
import tqdm
import pandas as pd
from matplotlib import pyplot as plt

from peek.utils.manage import Files
from peek.image.process import Snapshot, contour_center
from peek.image.analysis import Spectral, Preprocessing

class Mask(Spectral):
    def __init__(self, img):
        self.img = img
        self.gray = np.array([])
        self.masks = {}
        self.pars = {}
 
    def create_masks(self, pars):
        """
        algorithm to create masks of different regions in the nanocosms
        The algorithm nows:
        - sediments (detection works very well)
        - blue band (works very well too)
        - airspace between blue band and water surface. Not yet ideal
        - water surface, also not working perfectly

        Mostly the subroutines work by homogenizing surfaces by applying a 
        sequence of a minimum filter of input image, from which a mask is 
        calculated from the a color channel which ideally it has a very distinct 
        transition from the regions which are to be spearated. Afterwards, color
        ranges are selected from the whole image or a specific channel. 
        Then a max filter is calculated from this to make the region 
        more homogeneous
        [ ] this could be improved by including other color channels as well
        [x] or converting to greyscale beforehand

        Then two methods are currently available:
        1. Extract vertical peaks from the image with scipy.signal
        2. Extract extrema in vertical spectral ranges with scipy.signal

        Both methods work by passing 1D vertical slices to the respective function
        to get extrema or peaks
        [ ] Maybe this could again be improved by finding the closest inflection
            point or peak to the previous, thus noisy (up and down moevements 
            would be avoided) !!!
        
        From the resulting line, a mask is extended until the bottom or another 
        line which contains the region of interest.
        
        The good thing with this, is that we are only slightly dependent on a color range 
        because this changes with lighting conditions or sediment cover, the important
        thing necessary is a big enough change. 

        In a nutshell
        1. MIN -> RANGE -> MAX
        2. PEAK/SIGNAL detection
        3. MASKING

        A further option would be to fit geometric shapes to regions like the 
        water surface. Becaus it will follow an ellipsis every time. It should
        be "relatively" easy to fit an ellipsis if there are several constraints.
        """

        if isinstance(pars, str):
            if not os.path.exists(pars):
                pars = os.path.join(Files.load_settings_dir(), pars)
                
            self.pars = Files.read_settings(pars)

        assert isinstance(self.pars, dict), "input parameters must be of type dict"



    @staticmethod
    def apply_mask(img, mask, action="remove"):
        if action == "remove":
            mask = mask == False
            mask = mask.astype('uint8')
        if action == "show":
            mask = mask
        
        return cv.bitwise_and(img, img, mask=mask)

    def remove_blue_tape(
        self, blue_low=[0,0,0], blue_high=[0,0,0], 
        min_kernel_n=0, max_kernel_n=255, apply_mask=True
        ):
        mask = self.mrm(
            self.img, 
            min_kernel_n=min_kernel_n, 
            range_threshold=(np.array(blue_low), np.array(blue_high)), 
            max_kernel_n=max_kernel_n)

        self.masks['blue_tape'] = self.mask_from_top(mask)

        if apply_mask:
            self.img = self.apply_mask(self.img, self.masks['blue_tape'])

    @staticmethod
    def trim(img, t=None, b=None, l=None, r=None):
        if t is None:
            t = 0
        if b is None:
            b = img.shape[0]
        if l is None:
            l = 0
        if r is None:
            r = img.shape[1]

        return img[t:b, l:r, :]

    def mask_sediment(self, y_offset=0, min_kernel_n=1, max_kernel_n=1,
                      gray_low=0, gray_high=255, peak_height=100, peak_width=50,
                      apply_mask=True):

        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        mask = self.mrm(
            gray[y_offset:], 
            min_kernel_n=min_kernel_n,
            range_threshold=(gray_low, gray_high),
            max_kernel_n=max_kernel_n)

        # detect peaks
        left, right = self.detect_vertical_peaks(mask, height=peak_height, 
                                                 width = peak_width)

        # redraw mask based on peak analysis
        # using np.zeros instead of np.ones with fill=1 instead of fill=0 
        # inverts the process
        newmask = self.extend_horiz_border(
            left, img=np.zeros(gray.shape), towards="bottom", 
            y_offset=(y_offset, y_offset), fill=1)

        self.masks['sediment'] = newmask
        
        if apply_mask:
            self.img = self.apply_mask(self.img, self.masks['sediment'])

    def mask_airspace(self, y_offset=0, min_kernel_n=1, max_kernel_n=1,
                      gray_low=0, gray_high=255, peak_height=100, peak_width=50,
                      apply_mask=True):

        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        mask = self.mrm(
            gray[:y_offset], 
            min_kernel_n=min_kernel_n,
            range_threshold=(gray_low, gray_high),
            max_kernel_n=max_kernel_n)

        # detect peaks
        left, right = self.detect_vertical_peaks(mask, height=peak_height, 
                                                 width=peak_width)

        newmask = self.extend_horiz_border(
            right, img=np.zeros(gray.shape), towards="top", 
            y_offset=(0, 0), fill=1)
        
        self.masks['airspace'] = newmask

        if apply_mask:
            self.img = self.apply_mask(self.img, self.masks['airspace'])

    def mask_water_surface(self, y_offset=0, color_channel=2, min_kernel_n=1,
                           max_kernel_n=1, color_low=0, color_high=255, 
                           smooth_n=0, apply_mask=True):
        # detect peaks
        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        mask = self.mrm(
            self.img[:y_offset,:,color_channel], 
            min_kernel_n=min_kernel_n,
            range_threshold=(color_low, color_high),
            max_kernel_n=max_kernel_n)
        left, right = self.detect_vertical_extrema(
            mask, 
            smooth_n=smooth_n, 
            derivative=1)
        newmask = self.extend_horiz_border(
            left, img=np.zeros(gray.shape), towards=right, 
            y_offset=(0, 0), fill=1, smooth_n=smooth_n)

        self.masks['water_surface'] = newmask

        if apply_mask:
            self.img = self.apply_mask(self.img, self.masks['water_surface'])

class Param:
    def __init__(self, value, min=None, max=None, step=None):
            self._type = type(value)
            self._type.__init__(value)
            self.min = self._type(value / 4 if min is None else min)
            self.max = self._type(value * 2 if max is None else max)
            self.step = self._type(1 if step is None else step)

    def ParamClass(self, value):
        kwargs = self.__dict__.copy()
        _type = kwargs.pop("_type")
        ParamClass = type(self)
        return ParamClass(_type(value), **kwargs)

    def __mul__(self, other):
        return self.ParamClass(self._type(self) * other)

    def __div__(self, other):
        return self.ParamClass(self._type(self) / other)

    def __truediv__(self, other):
        return self.ParamClass(self._type(self) / other)

    def __add__(self, other):
        return self.ParamClass(self._type(self) + other)

    def __sub__(self, other):
        return self.ParamClass(self._type(self) - other)

    def __repr__(self):
        pcls = str(self._type).split("'")[1]
        return f"<Param[{pcls}]: {self._type(self)} [{self.min}-{self.max}] step={self.step}>"


class FloatParam(Param, float):
    def __new__(self, value, min=None, max=None, step=None) -> float:
        return float.__new__(self, value)

class IntParam(Param, int):
    def __new__(self, value, min=None, max=None, step=None) -> int:
        return int.__new__(self, value)


class Detector():

    @staticmethod
    def mask_image(img, masker, parfile, mask=None):
        # mask images
        m = masker(img)
        
        if mask is None:
            m.create_masks(pars=parfile)

        if mask is not None:
            m.img = mask.trim(img, **mask.pars['trim'])
            m.apply_multi(masks=mask.masks)

        return m
                
    @staticmethod
    def find_neighbors(t, tags, max_dist, closest=True):
        p = np.array([t["xcenter"], t["ycenter"]])
        points = np.array([tags.xcenter, tags.ycenter]).T
        abdist = points-p
        distance = np.sqrt(np.sum(abdist ** 2, axis=1) )
        if not closest:
            return np.where(distance < max_dist)[0]
        
        # return the point with the closest diagonal distance the is not
        # the point itself
        try:
            nb = np.argsort(distance)[1]
        except IndexError:
            nb = None
        return nb

    @staticmethod
    def predict(classifier, tag):
        features = [tag[f] for f in classifier.features]
        x = np.array(features).reshape((1, len(features)))
        nanfeatures = [f for f, xf in zip(classifier.features, features) if np.isnan(xf)]
        if len(nanfeatures) != 0:
            warnings.warn(f"{nanfeatures} were nan. Labelled as 'error'.")
            plabel = "error"
            pproba = np.repeat([[np.nan]], len(classifier.classes_), axis=1)
        else:
            pproba = classifier.predict_proba(x)
            plabel = classifier.predict(x)
        return plabel, pproba

    @classmethod
    def non_maximum_surpression(cls, classifier, tag, neighbor):
        iou = tag["neighbor_iou"]

        plabel_t, pproba_t = cls.predict(classifier, tag)
        
        # return early if iou is zero
        if iou > 0:
            plabel_nb, pproba_nb = cls.predict(classifier, neighbor)
        else:
            return plabel_t[0], pproba_t.max()
        
        # non maximum surpression
        if iou > 0.5 and plabel_t[0] == plabel_nb[0]:
            if pproba_t.max() > pproba_nb.max():
                label = "duplicate"
                prob = None
            else:
                label = plabel_t[0]
                prob = pproba_t.max()
        else:
            label = plabel_t[0]
            prob = pproba_t.max()

        return label, prob
    
    def make_predictions(self, tags, classifier):

        with tqdm.tqdm(total=tags.max_len, desc="predicting") as pbar:
            predictions = []
            probabilities = []

            for i in range(tags.max_len):
                t = tags.get_tag(i)
                n = tags.get_tag(t["closest_neighbor"])
                label, prob = self.non_maximum_surpression(classifier, t, n)

                predictions.append(label)
                probabilities.append(prob)

                pbar.update(1)

        tags.pred = predictions
        tags.prob = probabilities

        assert tags.is_equal_properties_lengths()
        
        return tags

    def analyze_tags(self, tags):
        """
        wrapper around analyze tag method specified by the user
        """

        tags.reset_extra_props()

        with tqdm.tqdm(total=tags.max_len, desc="analyzing") as pbar:
            new_tag_props = []
            for i in range(tags.max_len):
                # find clusters in threshold image with direct connectivity
                t = tags.get_tag(i)
                
                # find potential neighbors
                max_dist = np.sqrt(2 * self.margin ** 2)
                neighbor = self.find_neighbors(t, tags, max_dist, closest=True)
                nt = tags.get_tag(neighbor)

                props = self.analyze_tag(t, neighbor=(neighbor, nt))

                new_tag_props.append(props)
                # add props to tags

                pbar.update(1)
            
            for i in range(tags.max_len):
                props = new_tag_props[i]
                _ = [tags.add(key, value) for key, value in props.items()]
        
        assert tags.is_equal_properties_lengths()

        return tags

    def filter_tags(self, tags):
        """
        wrapper around test tag method specified by the user.
        Returns the ids of kept tags
        """
        drop_tags = []
        kept_tags = []
        with tqdm.tqdm(total=tags.max_len, desc="filtering") as pbar:

            for i in range(tags.max_len):
                t = tags.get_tag(i)
                keep = self.test_tag(t)
                
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

    def re_analyze_tags(self, tagger, annotations: pd.DataFrame):
        """
        convenience function to re-analyze existing tags from an Annotations
        class Pandas data-frame.
        """

        # convert annotations (pandas df) to Tagger class
        tags = tagger()
        tags.import_annotations(annotations)

        # analyze the tags
        tags = self.analyze_tags(tags)

        # make sure ids are equal before merging.
        tag_id_properties = list(tagger().__dict__.keys())
        for tip in tag_id_properties:
            matching = annotations[tip].values == np.array(getattr(tags, tip))
            eq = all(matching)
            assert eq, f"{tip} has non matching entries"
         
        setattr(tags, "label", annotations["label"].values)
        setattr(tags, "img_path", annotations["img_path"].values)
        setattr(tags, "image_hash", annotations["image_hash"].values)
        setattr(tags, "analysis", annotations["analysis"].values)
        setattr(tags, "time", annotations["time"].values)
        
        # filter tags
        fltr = self.filter_tags(tags)        
        tags = tags.apply_filter(fltr)
        
        return tags

    def analyze_tag(self, tag):
        raise NotImplementedError("you must write a custom 'analyze tag' method")

    def test_tag(self, tag):
        raise NotImplementedError("you must write a custom 'test tag' method")

    @staticmethod
    def difference(images, smooth=1, duplicates=False):
        """
        calculates the RGB differences between every two consecutive images.
        The last difference is the diff between last and first image
        """
        # changing the dtype from uint to int is very important, because
        # uint does not allow values smaller 0
        kernel = np.ones((smooth,smooth),np.float32)/smooth**2
        images = np.array([cv.filter2D(i, -1, kernel) for i in images], dtype=int)
        # ims = np.array([i.img for i in imlist], dtype=int)
        diff = np.diff(images, n=1, axis=0)

        if not duplicates:
            diffs = np.where(diff > 0, diff, 0)
        else:
            diffs = np.abs(diff)

        return [diffs[i,:,:,:].astype('uint8') for i in range(len(diffs))]        

    @staticmethod
    def get_contours(img, threshold):
        cnts = cv.findContours(img, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        cnts_select = []
        for c in cnts:
            # fit a bounding box to the contour
            if c.shape[0] > threshold:            
                cnts_select.append(c)

        return cnts_select

    @staticmethod
    def pass_tests(dict):
        return dict

    @staticmethod
    def get_contour_centers(contours):
        points = []
        for c in contours:
            box = cv.boundingRect(c)
            center = (box[0] + int(np.round(box[2]/2)), 
                      box[1] + int(np.round(box[3]/2)))
            points.append(center)
        
        return points


    @classmethod
    def find_pois(cls, img, filter_fun=None, filter_args={}):

        contours, hierarchy = cv.findContours(img, cv.RETR_TREE, 
                                              cv.CHAIN_APPROX_SIMPLE)

        if filter_fun is not None:
            contours = filter_fun(contours, **filter_args)

        points = cls.get_contour_centers(contours)

        return points, contours

    @staticmethod
    def contours_list_to_dict(contours, hierarchy):
        contour_dict = {}
        for c, h in zip(contours, range(len(contours))):
            contour_dict.update(
                {h: {"contour": c, "hierarchy": hierarchy[0][h, :]}}
            )

        return contour_dict
    
    @staticmethod
    def contours_dict_to_list(contours):
        contour_list = []
        for key, c in contours.items():
            contour_list.append(c["contour"])
        
        return contour_list
    
    @staticmethod
    def draw_contours_on_white(img, contours, show_plots=False):
        img = np.zeros(shape=img.shape, dtype="uint8")

        for c in contours:
            img = cv.drawContours(img, [c], 0, 255, cv.FILLED)
        
        if show_plots:
            plt.imshow(img)
            plt.show()

        return img
    
    @staticmethod
    def get_iou(bb1, bb2):
        """
        Calculate the Intersection over Union (IoU) of two bounding boxes.

        Parameters
        ----------
        bb1 : dict
            Keys: {'x1', 'x2', 'y1', 'y2'}
            The (x1, y1) position is at the top left corner,
            the (x2, y2) position is at the bottom right corner
        bb2 : dict
            Keys: {'x1', 'x2', 'y1', 'y2'}
            The (x, y) position is at the top left corner,
            the (x2, y2) position is at the bottom right corner

        Returns
        -------
        float
            in [0, 1]
        """
        bb1 = bb1.copy()
        bb2 = bb2.copy()
        
        bb1["x1"] = bb1["x"]
        bb1["x2"] = bb1["x"] + bb1["width"]
        bb1["y1"] = bb1["y"]
        bb1["y2"] = bb1["y"] + bb1["height"]

        bb2["x1"] = bb2["x"]
        bb2["x2"] = bb2["x"] + bb2["width"]
        bb2["y1"] = bb2["y"]
        bb2["y2"] = bb2["y"] + bb2["height"]

        assert bb1['x1'] < bb1['x2']
        assert bb1['y1'] < bb1['y2']
        assert bb2['x1'] < bb2['x2']
        assert bb2['y1'] < bb2['y2']

        # determine the coordinates of the intersection rectangle
        x_left = max(bb1['x1'], bb2['x1'])
        y_top = max(bb1['y1'], bb2['y1'])
        x_right = min(bb1['x2'], bb2['x2'])
        y_bottom = min(bb1['y2'], bb2['y2'])

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        # The intersection of two axis-aligned bounding boxes is always an
        # axis-aligned bounding box
        intersection_area = (x_right - x_left) * (y_bottom - y_top)

        # compute the area of both AABBs
        bb1_area = (bb1['x2'] - bb1['x1']) * (bb1['y2'] - bb1['y1'])
        bb2_area = (bb2['x2'] - bb2['x1']) * (bb2['y2'] - bb2['y1'])

        # compute the intersection over union by taking the intersection
        # area and dividing it by the sum of prediction + ground-truth
        # areas - the interesection area
        iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
        assert iou >= 0.0
        assert iou <= 1.0
        return iou
    
    @classmethod
    def get_overlapping_contours(cls, tags, iou_threshold: float=0.5):
        """
        find overlapping tag boxes.
        Caution! This function is slow. It scales with the square of the 
        number of detections. 
        """
        ious = []
        for i in range(tags.max_len):
            ious_ = []
            for j in range(tags.max_len):
                iou = cls.get_iou(tags.get_tag(i), tags.get_tag(j))
                if iou > iou_threshold:
                    if i == j:
                        continue
                    ious_.append((j, iou))
            ious.append(ious_)

        return ious

    @staticmethod
    def get_neighbors(ious, tag_id: int):
        """
        will get the cluster of partially overlapping tag boxes. Due to recursion
        it will go on until no tag box that matches the iou_threshold is found
        to obtain ious use self.get_overlapping_countours()
        """
        neighbors = []
        def recurse_neighbors(tid: int):
            for nb in ious[tid]:
                nid, iou = nb
                if nid == tid:
                    continue

                if nid in neighbors:
                    continue
                
                neighbors.append(nid)
                recurse_neighbors(nid)

        recurse_neighbors(tag_id)
        return neighbors

    @staticmethod
    def get_closest_neighbor(ious):
        closest_neighbors = []
        for i, nbs in enumerate(ious):
            if len(nbs) == 0:
                closest_neighbors.append((None, 0.0))
                continue
            max_nb = np.argmax([iou for _, iou in nbs])
            closest = nbs[max_nb]
            closest_neighbors.append(closest[0])

        return closest_neighbors
    
    @staticmethod
    def group_bounding_boxes(contours, group_threshold=1, eps=2):
        rects = []
        for c in contours:
            # fit a bounding box to the contour
            rects.append(cv.boundingRect(c))
            
        grouped_rects = cv.groupRectangles(rects, groupThreshold=group_threshold, eps=eps)

        return grouped_rects

    @staticmethod
    def close_contours(contours):
        hull_list = []
        for i in range(len(contours)):
            hull = cv.convexHull(contours[i])
            hull_list.append(hull)

        return hull_list

    @classmethod
    def generate_pois(cls, img, filter_fun=None, filter_args={}):

        contours, hierarchy = cv.findContours(img, cv.RETR_TREE, 
                                              cv.CHAIN_APPROX_SIMPLE)

        contours = cls.close_contours(contours)
        contours = cls.contours_list_to_dict(contours, hierarchy)

        if filter_fun is not None:
            contours = filter_fun(contours, **filter_args)

        # contours = cls.unite_fam(contours)
        contours = cls.contours_dict_to_list(contours)
        points = cls.get_contour_centers(contours)

        return points, contours

    # @classmethod
    # def preprocess(cls, img, poi, search_width, detector_fun, detector_args={}):
    #     # extract region of interest
    #     roi = cls.get_roi(img, poi, search_width)

    #     steps = detector_fun(roi, **detector_args)    
        
    #     return steps
    @staticmethod
    def preprocess(img, algorithm, algorithm_kwargs):
        
        if not callable(algorithm):
            algorithm = getattr(Preprocessing, algorithm)
        steps = algorithm(img, **algorithm_kwargs)

        return steps

    @staticmethod
    def plot_grid(plot_list):
        nrow = int(np.ceil(np.sqrt(len(plot_list))))
        ncol = int(np.ceil(len(plot_list) / nrow))
        fig, axes = plt.subplots(nrow, ncol, sharex=True, sharey=True)
        for i, ax in enumerate(it.product(range(nrow), range(ncol))):
            try:
                axes[ax[0], ax[1]].imshow(plot_list[i])
                axes[ax[0], ax[1]].set_title("step {}".format(i))
            except IndexError:
                pass
        plt.show()

    @staticmethod
    def get_roi(img, poi, search_width):
        # im = img.copy()
        y, x, c = img.shape
        pt1 = tuple([max(p - search_width, 0) for p in poi])
        pt2 = tuple([min(poi[0] + search_width, x), min(poi[1] + search_width, y)])
        return img[pt1[1]:pt2[1], pt1[0]:pt2[0], :]

    @classmethod
    def detect(cls, img, poi, search_width, detector_fun, detector_args={}, plot=False ):
        # extract region of interest
        roi = cls.get_roi(img, poi, search_width)

        steps = detector_fun(roi, **detector_args)    
        
        if plot:
            cls.plot_grid(steps)

        return steps

    @staticmethod
    def unite_fam(contours):
        delete = []
        for key, c in contours.items():
            parent = c['hierarchy'][3]
            # test if contour has parent (-1: no parent)
            if parent > -1:
                try:
                    contours[parent]["contour"] = np.row_stack((
                        contours[parent]["contour"], c["contour"]))
                    delete.append(key)
                except KeyError:
                    # key was already deleted before (during filtering)
                    pass

        for c in delete:
            del contours[c]

        return contours

    @staticmethod
    def unite_family(hierarchy, contours):
        if hierarchy is None:
            return []
        h = hierarchy.copy()[0]
        children = np.where(np.logical_and(h[:,2] == -1, h[:,3] != -1))[0].tolist()
        remove_childs = list()
        while len(children) > 0:
            parents = h[children,3].tolist()

            for p, c in zip(parents, children):
                contours[p] = np.row_stack((contours[p], contours[c]))

            h = np.delete(h, children, axis=0)
            remove_childs.extend(children)
            # children = np.where(h[:,2] == -1)[0].tolist()
            children = np.where(np.logical_and(h[:,2] == -1, h[:,3] != -1))[0].tolist()


        remove_childs.sort(reverse=True)
        for child in remove_childs:
            del contours[child]

        return contours

    @staticmethod
    def find_ellipses_in_contours(img, contours, draw=False):
        """
        only consider contours whose area can be determined. Otherwise they are
        of no use. The if else conditions can remain hardcoded, because they are the
        absolute minimal requirements for determining an ellipsis.
        """
        roi = img.copy() 
        center = np.array(Snapshot.get_center_2D(roi))
        properties = []
        for i, c in enumerate(contours):
            m = cv.moments(c)
            
            if len(c) >= 5:
                props = {}
                e = cv.fitEllipse(c)
                props['id'] = i
                props['distance'] = np.linalg.norm(np.array(e[0]) - center) 
                props['area'] = m['m00'] 
                props['xcenter'] = e[0][0]
                props['ycenter'] = e[0][1]
                props['len_minor'] = e[1][0]
                props['len_major'] = e[1][1]
                props['angle'] = e[2]
                properties.append(props)
                
                if draw:
                    # for p in range(c.shape[0]):
                    #     roi = cls.draw_cross(
                    #         roi, c[p][0][0], c[p][0][1], 1, 
                    #         color=(0, 100,0))
                    roi = cv.ellipse(roi, e, (0,255,0), 1)
                    roi = Snapshot.draw_cross(
                        roi, round(e[0][0]), round(e[0][1]), 1, 
                        color=(0,255,0))
            
            elif len(c) >= 4:
                if draw:
                    roi = cv.drawContours(roi, contours, i, (0,200,200), 1)
            
            elif m['m00'] == 0:
                if draw:
                    roi = cv.drawContours(roi, contours, i, (255,0,0), 1)

        return roi, properties, contours
        
    @staticmethod
    def select_and_sort(zipper, by):
        select = [(p[by], p, c) for p, c in zipper if p['select']]
        return [(p, c) for by, p, c in sorted(select)]
    
class Tagger():
    def __init__(self):
        self.tag_box_thresh_ids = []
        self.img_path = []
        self.x = []
        self.y = []
        self.width = []
        self.height = []
        self.xcenter = []
        self.ycenter = []

    def new(self, tag):
        setattr(self, tag, [])

    def reset_extra_props(self):
        standardprops = type(self)().__dict__.keys()
        currentprops = list(self.__dict__.keys())
        for key in currentprops:
            if key not in standardprops:
                delattr(self, key)

    def import_annotations(self, annotations: pd.DataFrame):
        for c in annotations.columns:
            if hasattr(self, c):
                setattr(self, c, list(annotations[c].values))

        assert self.is_equal_properties_lengths()

    def export_annotations(self):
        return pd.DataFrame(self.__dict__)

    def add(self, tag, value):
        if not hasattr(self, tag):
            self.new(tag)
        getattr(self, tag).append(value)

    def get_tag(self, i):
        if i is None:
            return None
        return {key: values[i] for key, values in self.__dict__.items()}

    def get(self, tag, i):
        return getattr(self, tag)[i]

    def set_none(self, keys=[]):
        for k in keys:
            getattr(self, k).append(None)

    def drop_tags(self, properties: list = [], drop_ids: list = []):
        for p in properties:
            prop = getattr(self, p)
            new_prop = [v for i, v in enumerate(prop) if i not in drop_ids]
            setattr(self, p, new_prop)

    def apply_filter(self, index):
        # create new tagger instance
        tags = type(self)()

        # get properties of self
        for key, value in self.__dict__.items():           
            # and set to new instance
            va = np.array(value)[index]
            setattr(tags, key, va.tolist())

        return tags

    def get_tag_box_coordinates(self, contour, shape):
        xcenter, ycenter = contour_center(contour)
        y = ycenter - (shape[0] - 1) / 2 
        x = xcenter - (shape[1] - 1) / 2
        width, height = shape

        self.add("x", int(x))
        self.add("y", int(y))
        self.add("width", int(width))
        self.add("height", int(height))
        self.add("xcenter", xcenter)
        self.add("ycenter", ycenter)

    @property
    def len_properties(self):
        return {key:len(prop) for key, prop in self.__dict__.items()}

    @property
    def max_len(self):
        return np.max(list(self.len_properties.values()))

    def is_equal_properties_lengths(self):
        lens = np.array(list(self.len_properties.values()))
        return all(lens[0] == lens)