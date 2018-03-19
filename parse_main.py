# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urllib.request, urllib.error
from urllib.request import urlopen
import json
import datetime
import hashlib
import os
import codecs

# import BeautifulSoup library
from bs4 import BeautifulSoup
# import css parse function
#import parse_css as pc

# メインのURL
mainURL = "http://www.okayama-opendata.jp/opendata/ga110Action.action?lnkOptionsBean.txtKeyword=&currentPage=__PAGE__&pageCount=13&searchString=q%3D%28organization%3A33203%29&paramName=&action=clickLnkSelectedPage&cboSort=01&paramOrgName=33203&paramTagsName=&paramFormatName=&paramLicenseName=&rssUrl=http%3A%2F%2Fwww.okayama-opendata.jp%2Fckan"
# datasetURL
urlDataSetBase = "http://www.okayama-opendata.jp/opendata/ga120PreAction.action?keyTitle=__KEYTITLEID__&datasetId=__DATASETID__"
# resourceURL
urlResBase = "http://www.okayama-opendata.jp/opendata/ga130PreAction.action?keyTitle=__KEYTITLEID__&resourceId=__RESID__&datasetId=__DATASETID__"

# start page (the minimum page is 1)
IDX_START = 1

# 読み込みページ数
count_page = 1

# パースメインメソッド
def parseNews(news_url):
    """
        引数のURLをパースし、結果をリストに詰めます。
        成功の場合Trueを返し、
        引数のURLが存在しないなど失敗の場合Falseを返します
    """

    try:
        html = urlopen(news_url)
    except:
        return None

    soup = BeautifulSoup(html,"html.parser")
    listObj = soup.findAll('ul',{"class":"dataset-list"})[0]

    if listObj is None:
        return None

    items = listObj.findAll('li',{"class":"dataset-item-dataset"})
    if isinstance(items, type(None)) or not items:
        return None

    itemList = []
    for item in items:
        content = item.find('div',{"class":"dataset-content"})
        dtfmt = content.find('ul',{"class":"dataset-resources"})
        fmt = dtfmt.find('li').find('a').get('data-format')
        fmt = fmt.lower()
        if not (fmt == 'csv' or fmt == 'jpg'):
            continue

        name = content.find('h3',{"class":"dataset-heading"}).find('a').get_text()
        hiddenFld = content.find('div')
        inpDataSetID = hiddenFld.find('input',{"id":"datasetId"}).get('value')
        inpKeyTitle = hiddenFld.find('input',{"id":"keyTitle"}).get('value')
        datasetName = hiddenFld.find('input',{"id":"title"}).get('value')
        urlDataSet = urlDataSetBase.replace("__DATASETID__",inpDataSetID).replace("__KEYTITLEID__",inpKeyTitle)
        resourceIds = getResourceId(urlDataSet)

        arrayResIds = resourceIds.split(",")
        # resourceUrls
        resUrls = []
        for aId in arrayResIds:
            a_url = urlResBase.replace("__DATASETID__",inpDataSetID).replace("__KEYTITLEID__",inpKeyTitle).replace("__RESID__",aId)
            s_url = getResFileNm(a_url)
            a_resUrl = {
                    "file": s_url
                    }
            resUrls.append(a_resUrl)
            downloadFile(s_url, fmt, datasetName)

        # "news_type" : news_type.get_text(),
        itemData = {
                "dataType" : fmt,
                "name" : name,
                "datasetId" : inpDataSetID,
                "keyTitle" : inpKeyTitle,
                "resourceId" : resourceIds,
                "urlRes" : resUrls
                }

        # add to list
        itemList.append(itemData)

    return itemList

def getResourceId(url):
    try:
        html = urlopen(url)
    except:
        return None
    soup = BeautifulSoup(html,"html.parser")
    return soup.find('input',{"id":"datasetResourceId"}).get('value')

def getResFileNm(url):
    try:
        html = urlopen(url)
    except:
        return None
    soup = BeautifulSoup(html,"html.parser")
    plainValue = soup.find('div',{"class":"wrapper"}).find('p',{"class":"muted"}).find('a').get_text()
    ret = plainValue.replace('\r\n','').replace('\t','')
    return ret

def downloadFile(url, fileType, dirName):
    print('downloading.. ' + url)
    resFile = urlopen(url)
    tmp = url.split('/')
    fileName = tmp[-1]
    dirPath = './' + fileType + '/' + dirName + '/'

    # if dir not exists, make it.
    mkDir(dirPath)

    # download it
    path =  dirPath + fileName
    with open(path,'wb') as output:
        output.write(resFile.read())

    # parse csv
    if fileType == 'csv':
        parseCsv(dirName, fileName)

NAME = 'name'
ADDRESS = 'address'
TEL = 'tel'
FAX = 'fax'
URL = 'url'
MEMO = 'memo'
ALT = 'alt'
LON = 'lon'

def parseCsv(dirName, fileName):
    dirInPath = './csv/' + dirName + '/'
    mkDir('./csv/')
    mkDir(dirInPath)
    dirOutPath = './json/' + dirName + '/'
    mkDir('./json/')
    mkDir(dirOutPath)

    fileNameIn = dirInPath + fileName
    fileNameOut = dirOutPath + fileName.replace('.csv', '.json')

    jsnObj = []
    fin = None
    fout = None
    try:
        fin  = codecs.open(fileNameIn, 'r', 'shift_jis')
        fout = codecs.open(fileNameOut, 'w', 'utf-8')
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
                    print('head: ' + str(head))
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

def mkDir(dirPath):
    if not os.path.exists(dirPath) and not os.path.isdir(dirPath):
        print ("dir not exists.")
        os.mkdir(dirPath)

# parse start
print("start..")
print(datetime.datetime.now())

# パース結果を詰めるリスト
itemList = []

# roopパース
index = IDX_START
while IDX_START <= index and index <= int(count_page):
    # パース対象ページのURLを取得
    targetUrl = mainURL.replace("__PAGE__", str(index) )

    # 読み込んでパース
    result = parseNews(targetUrl)
    if result is None:
        break;
    else:
        itemList.extend(result)

    # 経過をログ出力
    print("page index is " + str(index))

    index +=1

# パース結果をjson形式で出力
jsonString = json.dumps(itemList, ensure_ascii=False, indent=4)
nowfmt = datetime.datetime.now().strftime("%Y%m%d")
output_json_file = "tsuyama_" + nowfmt + ".json"
with open(output_json_file, "w") as fh:
    fh.write(jsonString)

# finish
print("page index is " + str(index))
print("finish parse and output json file.[" + output_json_file + "]")
print(datetime.datetime.now())
