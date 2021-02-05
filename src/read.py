# ======= read images and qr code and store in subfolders =====================
# takes long time
from image.process import Session

path = "../data/pics/20210118/"
s = Session(path)
s.read_images(stop_after=None)

path = "../data/pics/20210121/"
s = Session(path)
s.read_images(stop_after=None)

path = "../data/pics/20210125/"
s = Session(path)
s.read_images(stop_after=None)

path = "../data/pics/20210128/"
s = Session(path)
s.read_images(stop_after=None)


# Next Steps:
# - [ ] write code that moves all images out of subfolders (for first sessions) [easy]
# - [ ] Control QR codes
# - [ ] manually label QR codes which could not be read
# - [ ] write cluster script to process all images at once. This will be crucial 
#       if I want to reanalyze somethings