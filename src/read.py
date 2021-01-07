# TODO: Split file into scripts which can be executed in any shell


# ======= read images and qr code and store in subfolders =====================
# takes long time
from imrpoc import Series, Image, Session, Annotations
import pickle
path = "../../data/pics/20201217/"

ses = Session(path)
ses.read_images()


# improvements:
# + TODO: control QR codes
# + TODO: fix QR codes that could not be read
