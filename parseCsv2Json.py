import os
import codecs

import util as ut
import json

TMP_DIR = ut.TMP_DIR
CSV_DIR = TMP_DIR + 'csv/'

# csv header's column name
NAME = 'name'
ADDRESS = 'address'
TEL = 'tel'
FAX = 'fax'
URL = 'url'
MEMO = 'memo'
ALT = 'alt'
LON = 'lon'

def parseCsv(dirName, fileName):
    dirInPath = CSV_DIR + dirName + '/'
    ut.mkDir(CSV_DIR)
    ut.mkDir(dirInPath)

    JSON_DIR = TMP_DIR + 'json/'
    dirOutPath = JSON_DIR + dirName + '/'
    ut.mkDir(JSON_DIR)
    ut.mkDir(dirOutPath)

    fileNameIn = dirInPath + fileName
    fileNameOut = dirOutPath + fileName.replace('.csv', '.json')

    jsnObj = []
    fin = None
    fout = None
    try:
        fin  = codecs.open(fileNameIn, 'r', 'shift_jis', 'ignore')
        fout = codecs.open(fileNameOut, 'w', 'utf-8', 'ignore')
        print("convert to json..")

        idxs = {
            NAME : None,
            ADDRESS : None,
            TEL : None,
            FAX : None,
            URL : None,
            MEMO : None,
            ALT : None,
            LON : None
        }

        for i, row in enumerate(fin):
            if i == 0:
                heads = row.split(',')
                for idx, item in enumerate(heads):
                    head = getHead(item)
                    if head is not None:
                        idxs[head] = idx
            else:
                dt = row.split(',')
                j = {
                    NAME : getColValue(NAME, idxs, dt),
                    ADDRESS : getColValue(ADDRESS, idxs, dt),
                    TEL : getColValue(TEL, idxs, dt),
                    FAX : getColValue(FAX, idxs, dt),
                    URL : getColValue(URL, idxs, dt),
                    MEMO : getColValue(MEMO, idxs, dt),
                    ALT : getColValue(ALT, idxs, dt),
                    LON : getColValue(LON, idxs, dt)
                }
                jsnObj.append(j)

        jsonStr = json.dumps(jsnObj, ensure_ascii=False, indent=4)
        fout.write(jsonStr)
        return fileNameOut
    except Exception as e:
        print(e)
        return
    finally:
        if fout is not None:
            fout.close()
        if fin is not None:
            fin.close()

def getHead(item):
    item = item.replace('"','').replace("'",'').rstrip('\n').strip()

    # colmun candidates
    name = ['名称', '施設名', '分団名']
    address = ['住所', '地番', '機庫所在地']
    tel = ['TEL', '電話番号']
    fax = ['FAX']
    url = ['URL']
    memo = ['設置場所', '備考', '備考1']
    alt = ['世界_10進_Y']
    lon = ['世界_10進_X']

    if item in name:
        return NAME
    if item in address:
        return ADDRESS
    if item in tel:
        return TEL
    if item in fax:
        return FAX
    if item in url:
        return URL
    if item in memo:
        return MEMO
    if item in alt:
        return ALT
    if item in lon:
        return LON

    return None

def getColValue(key, idxs, row):
    idx = idxs[key]
    if idx == None:
        return None
    else:
        val = row[idx].replace('"','').replace("'",'').rstrip('\n').strip()
        return val
