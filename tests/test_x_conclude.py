import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import shutil

def test_x_conclude():
    shutil.rmtree('data/pics/test/00010101')