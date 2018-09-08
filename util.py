import os

# for local
# TMP_DIR = './tmp/'
# for lambda
TMP_DIR = '/tmp/'

def mkDir(dirPath):
    if not os.path.exists(TMP_DIR):
        os.mkdir(TMP_DIR)

    if not os.path.exists(dirPath) and not os.path.isdir(dirPath):
        os.mkdir(dirPath)

def mkDirNameText(path, dirName):
    path = path + "dirname.txt"
    if not os.path.exists(path):
        with open(path, mode='w') as f:
            f.write(dirName)
    
