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

print('processing {}'.format(args.input))
i.process_image(
    file_name=os.path.basename(args.input), 
    delete_old=args.delete_original,
    **params)

print("read QR code: {}".format(i.id))

# Next Steps:
# - [ ] write code that moves all images out of subfolders (for first sessions) [easy]
# - [ ] Control QR codes
# - [ ] manually label QR codes which could not be read
# - [ ] write cluster script to process all images at once. This will be crucial 
#       if I want to reanalyze somethings