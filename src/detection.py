import os
import pandas as pd
import argparse

from utils.manage import Files
from image.process import Series
from image.analysis import Annotations
from image.detectors.movement_edge import MovementEdgeDetector

parser = argparse.ArgumentParser(description='Carry out object detection on two images of a Series')
parser.add_argument('path' , type=str, help='path to images')
parser.add_argument('config', type=str, help='path to config file used for analysis')
parser.add_argument('-i1', '--image1', type=int, nargs='?', help='list of images to process', default=0)
parser.add_argument('-i2', '--image2', type=int, nargs='?', help='list of images to process', default=-1)
parser.add_argument('-b', '--backup', type=str, nargs='?', help='path to backup folder', default='')
parser.add_argument('-s', '--search_radius', type=int, nargs='?', help='radius of search box', default=50)
parser.add_argument('-r', '--blur', type=int, nargs='?', help='detector setting blur', default=5)
parser.add_argument('-t', '--threshold', type=int, nargs='?', help='detector setting threshold', default=10)
args = parser.parse_args()

# load images
s = Series(args.path)
img1 = s.images[args.image1]
img2 = s.images[args.image2]
nano = os.path.basename(args.path)

# initialize detector
detector = MovementEdgeDetector()

# tag image
tags = detector.tag_image(
    img1.img, img2.img, 
    dect_args={'blur':args.blur, 'thresh':args.threshold}, 
    parfile=args.config,
    search_radius=args.search_radius)

# export tags
a = Annotations(img1, 'moving_edge', tag_db_path="")
a.read_new_tags(pd.DataFrame(tags.__dict__))
if args.backup != '':
    Files.copy_files(args.path, args.backup, ex1='.tiff', ex2="PNAN")


# to customize it is recommended to write a new detector class under 
# image.detectors in the same style as motion and movement_edge
# then only a new detector has to be initialized
# this script can also be worked on a cluster very well. Nice and scalable
# next steps:
# - run analysis over one complete day (takes very long)
# - postprocess the tags and classify culex and Daphnia based on
#   ratios of major and minor axis
#   Also: Discard signals which are too small
# - write cluster scripts to process days