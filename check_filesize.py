import os
import glob
import shutil
from PIL import Image

CONV_DIR = "./jpg/conv/"
shutil.rmtree(CONV_DIR, ignore_errors=True)
if not os.path.exists(CONV_DIR) and not os.path.isdir(CONV_DIR):
    print ("dir not exists.")
    os.mkdir(CONV_DIR)

files = glob.glob('./jpg/*.jpg')
for f in files:
    filename = os.path.basename(f)
    filepath = './jpg/' + filename

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
