import os
import glob
import shutil
from PIL import Image

import util as ut

JPG_DIR = ut.TMP_DIR + "jpg/"
JPG_OUT = ut.TMP_DIR + "jpg_out/"
CONV_DIR = JPG_DIR + "conv/"

def resizeImage():
    # delete files
    shutil.rmtree(JPG_DIR, ignore_errors=True)
    ut.mkDir(JPG_DIR)
    ut.mkDir(CONV_DIR)

    files = glob.glob(JPG_DIR + '*.jpg')
    for f in files:
        filename = os.path.basename(f)
        filepath = JPG_DIR + filename

        # copy2 the dir
        shutil.copy2(filepath, CONV_DIR)

    files = glob.glob(CONV_DIR + '*.jpg')
    for f in files:
        filename = os.path.basename(f)
        filepath = CONV_DIR + filename
        b = os.path.getsize(filepath)
        size = b/1024/1024
        sizeStr = str(size)
        # print(sizeStr + ':' + os.path(filename))
        if (size >= 1.0):
            print(sizeStr + " :" + filename)
            img = Image.open(filepath)
            scale = int(size)
            imgSml = img.resize( (int(img.width/scale), int(img.height/scale)) )
            imgSml.save(filepath)

def resizeImage(dirName, fileName):
    ut.mkDir(JPG_DIR)
    ut.mkDir(JPG_OUT)

    fileNameIn = JPG_DIR + dirName + '/' + fileName
    dirOutPath = JPG_OUT + dirName + '/'
    ut.mkDir(dirOutPath)

    try:
        # copy2 the dir
        shutil.copy2(fileNameIn, dirOutPath)

        filepath = dirOutPath + fileName
        b = os.path.getsize(filepath)
        size = b/1024/1024
        sizeStr = str(size)
        # print(sizeStr + ':' + os.path(filename))
        if (size >= 1.0):
            print(sizeStr + " :" + fileName)
            img = Image.open(filepath)
            scale = int(size)
            imgSml = img.resize( (int(img.width/scale), int(img.height/scale)) )
            imgSml.save(filepath)

        return filepath

    except Exception as e:
        print(e)
        return
