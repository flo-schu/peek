# ======= read images and qr code and store in subfolders =====================
# takes long time
from image.process import Session
import pickle
path = "../data/pics/20201217/"

s = Session(path)
s.read_images(stop_after=3)

# Next Steps:
# 1. write code that moves all images out of subfolders (for first sessions) [easy]
# 2. Control QR codes
# 3. manually label QR codes which could not be read
#
# improvements:
# + TODO: control QR codes
# + TODO: fix QR codes that could not be read

