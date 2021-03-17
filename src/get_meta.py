from exifread import process_file
from image.process import Image
import datetime as dt
import argparse

parser = argparse.ArgumentParser(description='Get meta data of image')
parser.add_argument('input' , type=str, help='path to image')
args = parser.parse_args()

with open(args.input, 'rb') as f:
    tags = process_file(f)


print("---------------- ALL TAGS -------------------------")
for key, value in tags.items():
    print(key, ' : ', value)

print("---------------- EXTRACTED ------------------------")
print("---------------- TIME -----------------------------")
t = tags['EXIF DateTimeOriginal']

ts = dt.datetime.strptime(t.values, "%Y:%m:%d %H:%M:%S")
date = ts.strftime('%Y%m%d')
print(ts, date)


print("---------------- ISO -----------------------------")
print("ISO:", tags['Image Tag 0x0037'].values)

print("---------------- Focal Length  -------------------")
print("Focal length:", tags['EXIF FocalLength'].values)

print("---------------- Exposure Time  ------------------")
print("Exposure Time:", tags['EXIF ExposureTime'].values)

print("---------------- F-Value  ------------------")
print("F-Value:", tags['EXIF FNumber'].values)

print("---------------- Aperture  ------------------")
print("Max Aperture:", tags['EXIF MaxApertureValue'].values)

print("---------------- Camera  ------------------")
print("Camera Model:", tags['Image Make'], tags['Image Model'].values)

