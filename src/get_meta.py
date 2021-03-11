from exifread import process_file
from image.process import Image
import datetime as dt

path = "../data/pics/20210223/PNAN7193.RW2"
# i = Image(path)
# i.read_raw()

# print(i.date)
# print(i.time)

f = open(path, 'rb')
tags = process_file(f)
t = tags['EXIF DateTimeOriginal']

ts = dt.datetime.strptime(t.values, "%Y:%m:%d %H:%M:%S")
date = ts.strftime('%Y%m%d')

print(ts, date)