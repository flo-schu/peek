# created by Florian Schunck on 20.08.2020
# Project: 2020_07_nanocosm_2
# Short description of the feature:
# 
# 
# ------------------------------------------------------------------------------
# Open tasks:
# TODO:
# 
# ------------------------------------------------------------------------------

from tifffile import imread

im = imread("./img/P8190098.tif", key=0)
im.shape