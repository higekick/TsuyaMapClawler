import os

# for local
#TMP_DIR = './tmp/'
# for lambda
TMP_DIR = '/tmp/'

def mkDir(dirPath):
    if not os.path.exists(dirPath) and not os.path.isdir(dirPath):
        os.mkdir(dirPath)
