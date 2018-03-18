# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urllib.request, urllib.error
from urllib.request import urlopen
import json
import datetime
import hashlib

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
count_page = 14

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
            downloadFile(s_url, fmt)

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

def downloadFile(url, fileType):
    print('downloading.. ' + url)
    resFile = urlopen(url)
    tmp = url.split('/')
    fileName = tmp[-1]
    path = './' + fileType + '/' + fileName
    with open(path,'wb') as output:
        output.write(resFile.read())

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
