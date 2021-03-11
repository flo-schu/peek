from image.process import Session
import argparse

parser = argparse.ArgumentParser(description='Carry out object detection on two images of a Series')
parser.add_argument('input' , type=str, help='path to image directory')
parser.add_argument('-n', '--number_files' , type=int, help='number of files to process', default=None)
args = parser.parse_args()

s = Session(args.input)
s.read_images(stop_after=args.number_files)

# Next Steps:
# - [ ] write code that moves all images out of subfolders (for first sessions) [easy]
# - [ ] Control QR codes
# - [ ] manually label QR codes which could not be read
# - [ ] write cluster script to process all images at once. This will be crucial 
#       if I want to reanalyze somethings