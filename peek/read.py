import argparse
from peek.image.process import Session
from peek.utils.manage import Files

parser = argparse.ArgumentParser(description='Carry out object detection on two images of a Series')
parser.add_argument('input' , type=str, help='path to image directory')
parser.add_argument('-f', '--file_id' , type=int, help='number of image in directory', default=None)
parser.add_argument('-p', '--img_params' , type=str, help='path to settings for image processing', default="")
parser.add_argument('-n', '--number_files' , type=int, help='number of files to process', default=None)
parser.add_argument('-d', '--delete_original' , type=bool, help='should the original image be deleted', default=False)
args = parser.parse_args()

params = Files.read_settings(args.img_params)

s = Session(args.input)
s.read_images(
    stop_after=args.number_files, 
    file_number=args.file_id, 
    delete_old=args.delete_original, 
    params=params
    )

# Next Steps:
# - [ ] write code that moves all images out of subfolders (for first sessions) [easy]
# - [ ] Control QR codes
# - [ ] manually label QR codes which could not be read
# - [ ] write cluster script to process all images at once. This will be crucial 
#       if I want to reanalyze somethings