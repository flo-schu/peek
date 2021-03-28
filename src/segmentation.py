import os
import pandas as pd
import argparse

from utils.manage import Files
from image.process import Image
from image.analysis import Annotations
from image.detectors.region_growing import RegionGrowingDetector

parser = argparse.ArgumentParser(description='Carry out object detection on two images of a Series')
parser.add_argument('input' , type=str, help='path to image')
parser.add_argument('-c', '--config', type=str, help='path to config file used for analysis', default='segmentation_default.json')
parser.add_argument('-b', '--backup', type=str, nargs='?', help='path to backup folder', default='')
parser.add_argument('-p', '--progress', type=bool, help='show progress bar', default=False)
parser.add_argument('-v', '--visualize', type=bool, help='should plots be visualized', default=False)
args = parser.parse_args()


sdir = Files.load_settings_dir()
config = Files.read_settings(os.path.join(sdir, args.config))
print("using settings:", config)

# load images
img = Image(args.input)
# ifelse statement 
# check if second img was imported, if no proceed with detector.tag_image
# if yes, use tag_images, or pass both images to list and 
# make checks in tag_image

# initialize detector
detector = RegionGrowingDetector()

# tag image
tags = detector.tag_image(
    img = img.img, 
    search_radius=config["search_radius"],
    detector_config=config["detector"], 
    filter_config=config["contour_filter"],
    mask_config=config["masking_config"],
    preprocess_config=config["preprocess"],
    progress_bar=args.progress,
    show_plots=args.visualize)

print('tagging complete')

# export tags
nano = os.path.basename(args.input)
a = Annotations(img, 'moving_edge', tag_db_path="")
a.read_new_tags(pd.DataFrame(tags.__dict__))
if args.backup != '':
    Files.copy_files(args.path, args.backup, ex1='.tiff', ex2="PNAN")

print("analysis complete.")

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