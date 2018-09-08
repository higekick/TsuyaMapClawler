# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urllib.request, urllib.error
from urllib.request import urlopen
import datetime
import hashlib
import os
import codecs
from multiprocessing import Process

# import BeautifulSoup library
from bs4 import BeautifulSoup

import parseCsv2Json as pcj
import resizeImage as rimg
import util as ut
import util_lambda as ul

# メインのURL
mainURL = "http://www.okayama-opendata.jp/opendata/ga110Action.action?lnkOptionsBean.txtKeyword=&currentPage=__PAGE__&pageCount=13&searchString=q%3D%28organization%3A33203%29&paramName=&action=clickLnkSelectedPage&cboSort=01&paramOrgName=33203&paramTagsName=&paramFormatName=&paramLicenseName=&rssUrl=http%3A%2F%2Fwww.okayama-opendata.jp%2Fckan"
# datasetURL
urlDataSetBase = "http://www.okayama-opendata.jp/opendata/ga120PreAction.action?keyTitle=__KEYTITLEID__&datasetId=__DATASETID__"
# resourceURL
urlResBase = "http://www.okayama-opendata.jp/opendata/ga130PreAction.action?keyTitle=__KEYTITLEID__&resourceId=__RESID__&datasetId=__DATASETID__"

# start page (the minimum page is 1)
# IDX_START = 1
IDX_START = int(os.environ['IDX_START'])

# 読み込みページ数
# COUNT_PAGE = 13
COUNT_PAGE = int(os.environ['COUNT_PAGE'])

TMP_DIR = ut.TMP_DIR

is_lambda = True

# パースメインメソッド
def parseMain(url, dummy):

    try:
        print("url:" + url)
        html = urlopen(url)
    except Exception as e:
        print("Http Error:" + e.args)
        return None

    soup = BeautifulSoup(html,"html.parser")
    listObj = soup.findAll('ul',{"class":"dataset-list"})[0]

    if listObj is None:
        return None

    items = listObj.findAll('li',{"class":"dataset-item-dataset"})
    if isinstance(items, type(None)) or not items:
        return None

    p = None
    for item in items:
        p = Process(target=processItem, args=(item, "dummy"))
        p.start()
    
    if p:
        p.join()

def processItem(item, dummy):
    content = item.find('div',{"class":"dataset-content"})
    dtfmt = content.find('ul',{"class":"dataset-resources"})
    fmt = dtfmt.find('li').find('a').get('data-format')
    fmt = fmt.lower()
    if not (fmt == 'csv' or fmt == 'jpg'):
        # only csv or jpg
        return

    name = content.find('h3',{"class":"dataset-heading"}).find('a').get_text()
    hiddenFld = content.find('div')
    inpDataSetID = hiddenFld.find('input',{"id":"datasetId"}).get('value')
    inpKeyTitle = hiddenFld.find('input',{"id":"keyTitle"}).get('value')
    datasetName = hiddenFld.find('input',{"id":"title"}).get('value')
    urlDataSet = urlDataSetBase.replace("__DATASETID__",inpDataSetID).replace("__KEYTITLEID__",inpKeyTitle)
    resourceIds = getResourceId(urlDataSet)

    arrayResIds = resourceIds.split(",")
    # p = None
    hashStr = datasetName.encode('utf-8')
    hashStr = hashlib.md5(hashStr).hexdigest()
    dirPath = TMP_DIR + fmt + '/' + hashStr + '/'

    for aId in arrayResIds:
        # p = Process(target=processDownload, args=(aId, inpDataSetID, inpKeyTitle, datasetName, fmt, "dummy"))
        # p.start()
        processDownload(aId, inpDataSetID, inpKeyTitle, datasetName, fmt, dirPath, hashStr, "dummy")
    # if p:
        # p.join()
    
    # upload dirname text
    ut.mkDirNameText(dirPath, datasetName)
    outpath = dirPath + 'dirname.txt'
    if fmt == 'csv':
        fmt = 'json'
    uploadPath = fmt + '/' + hashStr + '/' + 'dirname.txt'
    ul.uploadToBucketDirect(outpath, uploadPath)

def processDownload(aId, inpDataSetID, inpKeyTitle, datasetName, fmt, dirPath, hashStr, dummy):
    a_url = urlResBase.replace("__DATASETID__",inpDataSetID).replace("__KEYTITLEID__",inpKeyTitle).replace("__RESID__",aId)
    s_url = getResFileNm(a_url)
    downloadFile(s_url, fmt, datasetName, dirPath, hashStr)

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

def downloadFile(url, fileType, dirName, dirPath, hashStr):
    # print('downloading.. ' + url)
    resFile = urlopen(url)
    tmp = url.split('/')
    fileName = tmp[-1]


    # if dir not exists, make it. ./tmp/csv or ./tmp/jpg
    ut.mkDir(TMP_DIR + fileType)
    ut.mkDir(dirPath)

    # download it
    path =  dirPath + fileName
    with open(path,'wb') as output:
        output.write(resFile.read())

    outpath = ''
    if fileType == 'csv':
        # parse csv and convert to json
        outpath = pcj.parseCsv(hashStr, fileName)
        fileType = 'json'
    elif fileType == 'jpg':
        # resize jpg to small
        outpath = rimg.resizeImage(hashStr, fileName)

    # upload to s3 bucket
    if not isinstance(outpath,type(None)) and is_lambda:
        prefix = fileType + '/' + hashStr
        ul.uploadToBucket(outpath, prefix)

def main():
    # parse start
    print("start..")
    print(datetime.datetime.now())

    # delete s3 contents
    if is_lambda:
        ul.delDirInBucket()

    # roopパース
    index = IDX_START
    p = None
    while IDX_START <= index and index <= int(COUNT_PAGE):
        # 経過をログ出力
        print("page index is " + str(index))
        # パース対象ページのURLを取得
        targetUrl = mainURL.replace("__PAGE__", str(index) )
        # 読み込んでパース
        p = Process(target=parseMain, args=(targetUrl, 'dummy'))
        p.start()
        index +=1
    if p:
        p.join()

    # finish
    print("finish!")
    print(datetime.datetime.now())

# from local
if __name__ == '__main__':
    is_lambda = False
    main()

# from AWS lambda
def lambda_handler(event, context):
    is_lambda = True
    main()
