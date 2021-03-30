from image.process import Image
from utils.manage import Files
import argparse
import json
import os
import sys

parser = argparse.ArgumentParser(description='Carry out object detection on two images of a Series')
parser.add_argument('input' , type=str, help='path to image')
parser.add_argument('-p', '--img_params' , type=str, help='path to settings for image processing', default="")
parser.add_argument('-q', '--qr_params' , type=str, help='path to settings for image processing', default="qr_detect_default.json")
parser.add_argument('-d', '--delete_original' , type=bool, help='should the original image be deleted', default=False)
parser.add_argument('-t', '--thumbnail' , type=bool, help='create a thumbnail img of the region scanned for qr code', default=False)
parser.add_argument('-o', '--output_format', type=str, help='output format after reading .RW2 file', default="tiff")
args = parser.parse_args()

print('reading parameters ...')
sdir = Files.load_settings_dir()
print('reading settings from: ', sdir)
im_params = Files.read_settings(os.path.join(sdir, args.img_params))
qr_params = Files.read_settings(os.path.join(sdir, args.qr_params))
print('using image_settings:', json.dumps(im_params))
print('using qe_settings:', json.dumps(qr_params))

print('check if image file exists')
i = Image(args.input)

print('processing {}'.format(args.input))
i.process_image(
    file_name=os.path.basename(args.input), 
    delete_old=args.delete_original,
    qr_thumb=args.thumbnail,
    qr_params=qr_params,
    output_format=args.output_format,
    **im_params)

print("read QR code: {}".format(i.id))

# Next Steps:
# - [ ] write code that moves all images out of subfolders (for first sessions) [easy]
# - [ ] Control QR codes
# - [ ] manually label QR codes which could not be read
# - [ ] write cluster script to process all images at once. This will be crucial 
#       if I want to reanalyze somethings