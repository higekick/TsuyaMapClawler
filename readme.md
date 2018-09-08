Please install following.  

```
sudo pip3 install requests -t /path/to/project
sudo pip3 install beautifulsoup4 -t /path/to/project
sudo pip3 install Pillow -t /path/to/project
```

to test AWS lambda from local environment.
https://github.com/fugue/emulambda

to upload lambda zip
$ zip -X -r uploadlambda.zip *

## CSV column head canditates for converting json
* name
 - 名称
 - 施設名
 - 分団名
* address
 - 住所
 - 地番
 - 機庫所在地
* tel
 - TEL
 - 電話番号
* fax
 - FAX
* url
 - URL
* memo
 - 設置場所(AEDの場合)
 - 備考
 - 備考1-3
* alt 緯度
 - 世界_10進_Y
* lon 経度
 - 世界_10進_X

telに0868-がついていない場合はつける
電話のインテントに飛ばすため
