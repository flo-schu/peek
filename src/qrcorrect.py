# 1. get directory tree of all 999 subfolders
# 2. read images
# 3. downscale and cut out region where number of nano will be 
# 4. annotate with date, time and img name
# 5. save and label according to date, time and name in one folder
# 6. create CSV file with labels friom (5) in the same order (should be automatic due to date and time format YYYYMMDD_HHMM_NAME.tiff)
#    this should be kept and only updated with new unclear nanos, so that not everything has to be ran twice
# 7. read the file and move images from 999 to appropriate locations
from image.process import Image
from utils.manage import Files
import argparse
import os

parser = argparse.ArgumentParser(description='Carry out object detection on two images of a Series')
parser.add_argument('input' , type=str, help='path to image')
parser.add_argument('-p', '--img_params' , type=str, help='path to settings for image processing', default="")
parser.add_argument('-d', '--delete_original' , type=bool, help='should the original image be deleted', default=False)
args = parser.parse_args()

print('reading paramteters ...')
params = Files.read_settings(args.img_params)

print('check if file exists')
i = Image(args.input)