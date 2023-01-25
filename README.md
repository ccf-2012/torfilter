
# PT站过滤下载入库流程
* 这是一套基于日常使用pt站点的下片入库方案，可以某些条件过滤站点列出的条目，如果有一个自建的Plex/Emby影音库，可以查询哪些影片是库中缺少的。

整体流程如下：

![dataflow](https://ptpimg.me/07ivzz.png)

1. 种子列表过滤脚本`torfilter.js` 是一个油猴脚本，在PT站页面添加一些辅助过滤的功能，选中的种子可以提交信息给`dupapi.py`进行处理
2. `dupapi.py` 是一个api服务，可对提交来的信息在本地的媒体库中查重，并将下载链接交给qBittorrent启动下载，同时打上imdb信息标签
3. qBittorrent下载完成调用脚本将文件和imdb信息标签交 `torcp` 进行目录重新组织，参考 [这里的详细文档](https://github.com/ccf-2012/torcp/blob/main/qb%E8%87%AA%E5%8A%A8%E5%85%A5%E5%BA%93.md)
4. 组织好的媒体文件，Plex可刮削入库


## Last update:
* 2023.1.25: `--siteid-folder` for duapi, torss: 添加种子时建立 'Site_Id_IMDb' 目录，例如：aud_108375_tt1172571
* 2023.1.17: lemonhd (gazella, animate分类无效)
* 2023.1.14: torss
* 2022.12.14: hdc, hds
* 2022.12.13: 对在列表页没有IMDb信息的站点，取详情页获取IMDb信息再下载
* 2022.12.12: frds,beitai等站点支持；未作种，未曾下，列表页仅查重，查&下
* 2022.10.12: 支持Emby，支持pt站上种子详情页上查重和下载
* 2022.10.9: 新增本地查重下载服务 **dupapi** ，网页将种子信息提交进行查重，符合条件的推送下载器
* 2022.10.5: ob, ssd 在拷贝下载链接时，从控制面板中取passkey拼合形成下载链接
* 2022.10.5: IMDb 或 豆瓣 大于输入值
* 2022.10.4: 加入大小介于过滤，单位GB，使用`,`分隔；
* 2022.10.4: 使用Cookie保存参数
* 2022.9.28: 标题不含，描述不含，分别搜索，忽略大小写； 加入ob, ssd支持
* 2022.9.25: 支持pter, chd, ade种子列表过滤: 过滤: 未作种， 无国语，有中字，标题不含，以及imdb大于输入值 的种子


-----
# 种子列表过滤脚本 torfilter
![torfilterjs](https://ptpimg.me/d5l9yv.png)


## Greasy Fork 安装地址
* https://greasyfork.org/zh-CN/scripts/451748

## 功能
油猴脚本，在种子列表页中:
1. 过滤: 未作种，无国语，有中字，标题不含，描述不含，大小介于，IMDb/豆瓣大于输入值 的种子
    * 当前支持pter, chd, ade, ob, ssd, frds, beitai, ttg, hdc, hds, lhd
    * 大小介于的输入框中，单位为GB，使用`,` 或 `-` 分隔。填写 `0,20` 表示小于20GB的种子
2. 新增一列快速认领，当前仅支持猫站
3. 配合 dupapi.py 实现查重下载入库 (since 2022.10.9)

* 本脚本仅在打开的站点页面上进行过滤，对站点服务器无任何额外请求负担
* 在cookie中会保存参数，以便翻页时持有设置的值，不影响原cookie
* lhd中gazella模式和animate分类无效


### 列表页的查重与下载
* “仅查重” 与 “查&下” 都是通过后台dupapi进行;
* ob, ssd, aud, pter, ttg, hds 等站列表页有IMDb标识，torfilter会用IMDb来查重并在推送qbit下载时添加标签(tag)
* frds, chd, beitai, hdc等站在列表页没有IMDb链接信息，在种子详情页可能会获取到，则：
  - 在查重时，torfilter会使用种子名称提交查重，后台dupapi会以torcp解析种子名称后查找TMDb再进行查重。这种依赖种子名称查TMDb有可能失误；
  - 在下载时，torfilter将去获取种子详情页，并提取IMDb信息，之后再提交后台dupapi进行下载，这样也会在qbit中对种子加上标签；
  - 如果先点选了“仅查重”，再点“查&下”，则在下载时，会仅对“仅查重”时标绿的种子进行详情页的获取及下载，对于上述列表页没有IMDb信息的站，推荐如此操作下载，否则直接“查&下”将对可见列表中每个条目去站点获取详情页；
* 在“查&下”过程中，每个条目下载后有约2秒的间隔，在“仅查重”时则只有50ms；


### Note:
* 部分站不支持国语，中字标签搜索
* ob, chd, ssd, frds, hds 的下载链接无passkey，拼合usercp中的passkey构成下载链接
* 种子列表页面上无法取得imdb的(frds, chd, beitai, hdc)，以及列表页上无法取得下载链接的(hds)，会进入种子详情页获取信息，这会对站点发起拉取页面的操作，各站对拉取页面和种子不同的保护措施，请自行把握。


### 提交查重下载后，返回几种结果
* 提交下载后，页面中种子背景会改为若干种可能的颜色 ：
![3种结果](https://ptpimg.me/3cgnss.png)
> 图中filterapi，已改名dupapi，since 2022.10.12

1. 库中没有，提交qBittorrent下载了
2. 库中已有，跳过，不下载
3. TMDb没有查到，当前也是跳过不下载
4. dupapi无法提交给下载器出错时，返回400，在页面上显示红色
5. since 2022.10.12, 新增一种颜色`darkturquoise`，在种子列表页无法取得下载链接时，表示未重复但不下载


-----

# 本地下载入库api服务 dupapi

## 前置准备
1. python环境
```sh
# 下载
git clone https://github.com/ccf-2012/torfilter.git
cd torfilter
pip install -r requirements.txt
```

2. 填写 `config.ini` 信息
```sh 
cp config-sample.ini config.ini
vi config.ini
```

* 参考注释和示例，编写其中的各项信息：
```ini
[PLEX]
server_url=http://192.168.5.6:32400
; 取得Plex token的步骤： https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
server_token=E3-my-plex-token-CbVsY

; [EMBY]
; server_url=http://192.168.5.6:8096
; user=embyuser
; pass=embypass

[TMDB]
; 取得TMDb api key步骤: https://kb.synology.cn/zh-cn/DSM/tutorial/How_to_apply_for_a_personal_API_key_to_get_video_info
api_key=9e07s1bthetmdbapikey3c2674b093


[QBIT]
server_ip=192.168.5.199
port=8091
user=MyQbitUsername
pass=MyQbitPassword

```

## 建立本地Emby/plex条目数据库
> 每一次查重都现场从plex服务器中查询条目代价过大，所以这里是在本地建立 **sqlite** 数据库

* 运行初始化数据库命令，从自己的Plex/Emby服务器中获取所有条目，存储在本地 **sqlite** 数据库中，其间如果发现条目没有TMDb数据，将会现查并补全。
```sh
python dupapi.py --init-library
```
* 初始化命令运行完成后将会退出
* sqlite 数据库存在当前目录下的 `instance` 目录中，如果想要重新初始化，可直接 `rm -rf instance` 删除再重建
* 如果以非空库运行 `--init-library` 则原有数据会清除，如果要保留现有数据库中的数据添加新数据，可加 `--append` 参数
* 如果同时配置了Emby和Plex，则两个库内容都会添加

### 命令使用
```
python dupapi.py -h

usage: dupapi.py [-h] [--init-library] [-a] [--fill-tmdb] [--siteid-folder]

A torrent handler does library dupe check, add qbit with tag, etc.

options:
  -h, --help       show this help message and exit
  --init-library   init database with plex query.
  -a, --append     append to local database, without delete old data.
  --fill-tmdb      fill tmdb field if it miss.
  --siteid-folder  make Site_Id_Imdb parent folder.
```

### 例子
```sh
# 清空当前数据，读入Plex/Emby中的数据
python dupapi.py --init-library  

# 读入Plex/Emby中的数据，添加到当前数据库
python dupapi.py --init-library  --append
python dupapi.py --init-library  -a

# 对当前数据库，对TMDb缺失的进行查找补全
python dupapi.py --fill-tmdb

```

## 启动 dupapi 服务
* 如果不带参数执行 `dupapi.py` 则将启动 dupapi 服务，这是一个web api服务。
* 当前内置的监听端口为 `3006`，这个端口号是与 `torfilter.js` 中对应的。若要修改，则两边代码中对应查找修改。
* 当前过滤脚本 `torfilter.js` 会连接 `localhost` 中的 `dupapi`服务，如果部署在不同机器上，则在 `torfilter.js` 中查找修改。

* 启动 dupapi 服务：
```sh 
python dupapi.py
```

* 过滤脚本 `torfilter.js` 会发送的api请求相当于：
```sh
curl -i -H "Content-Type: application/json" -X POST -d '{"torname" : "The Frozen Ground 2013 1080p BluRay x265 10bit DTS-ADE", "imdb": "tt2005374", "downloadlink": "https://audiences.me/download.php?id=71406&...."}' http://localhost:3000/p/api/v1.0/dupedownload
```

### 注意：
* dupapi 服务设计为本地临时启用用途，暂无密码防护
* dupapi接受浏览器插件torfilter连接，会连themoviedb.org查TMDb，会连qbit下载器进行下载；所以需三方网络都通，特别地，连接TMDb查询，可能需配置 host 或 梯；
* dupapi当前对于剧集，没有分辨季与集，只要有就判重，可在详情页手动点下载。

-----

# torss
* torss用于通过站点提供的rss链接，结合种子详情页解析出IMDb信息，添加种子时同时添加IMDb标签
* torss所使用的qBit下载器，与dupapi共用 `config.ini` 中的设置
* torss在下载时也会进行查重，与dupapi同样使用 `instance` 子目录中的SQLite 数据库

## 前置准备
* 与前面dupapi部分相同


## 使用
```
python3 torss.py -h

usage: torss.py [-h] [-R RSS] [-s SINGLE_PAGE] [-c COOKIE] [--title-regex TITLE_REGEX] [--title-not-regex TITLE_NOT_REGEX] [--info-regex INFO_REGEX]
                [--info-not-regex INFO_NOT_REGEX] [--sleep SLEEP] [--add-pause] [--exclude-no-imdb] [--min-imdb MIN_IMDB] [--siteid-folder] [--init-rss-history]

A script to rss pt site, add torrent to qbit with IMDb id as a tag.

options:
  -h, --help            show this help message and exit
  -R RSS, --rss RSS     the rss link.
  -s SINGLE_PAGE, --single-page SINGLE_PAGE
                        fetch single torrent in detail page.
  -c COOKIE, --cookie COOKIE
                        the cookie to the detail page.
  --title-regex TITLE_REGEX
                        regex to match the rss title.
  --title-not-regex TITLE_NOT_REGEX
                        regex to not match the rss title.
  --info-regex INFO_REGEX
                        regex to match the info/detail page.
  --info-not-regex INFO_NOT_REGEX
                        regex to not match the info/detail page.
  --sleep SLEEP         sleep between each request of info page.
  --add-pause           Add torrent in PAUSE state.
  --exclude-no-imdb     Do not download without IMDb
  --min-imdb MIN_IMDB   filter imdb greater than <MIN_IMDb>.
  --siteid-folder       make Site_Id_Imdb parent folder.
  --init-rss-history    Init/Empty rss history table.
```
* 注： 不加 `--cookie` 不解析种子信息页，

## 示例
* 从rss链接中，逐个获取种子详情页，提取IMDb id并将种子发送至下载器，打上IMDB标签
```sh
python3 torss.py -R "https://some.pt.site/torrentrss.php?rows=10&..." -c "c_secure_uid=ABCDE; ....c_secure_tracker_ssl=bm9wZQ==" 
```

* 取单个页面，提取IMDb id并将种子发送至下载器，打上IMDB标签
```sh
python3 torss.py -i "https://some.pt.site/details.php?id=60381"  -c "c_secure_uid=ABCDE; ....c_secure_tracker_ssl=bm9wZQ==" 
```

* 标题中包含 x264 且以 ADE 结尾的，且非单集剧集(标题中不包含 'E07'这样的分集特征的)
```sh
python3 torss.py --title-regex 'x264.*[-@]?ADE$' --title-not-regex 'Ep?\d+' -R "https://some.pt.site/torrentrss.php?rows=10&tags=gf%zz&exp=90....."  -c "c_secure_uid=ABCDE; ....c_secure_tracker_ssl=bm9wZQ==" 
```

* 信息详情页可解析到更多信息，提供了 `--info-regex` 和 `--info-not-regex` 两个正则，比如下面例子是通过详情页信息过滤：有中字，非国语，且有IMDb的种子(仅作示例，部分站如观众和猫，建RSS链接时本身提供国语和中字标签的过滤)：
```sh
python3 torss.py --info-regex 'tags tzz' --info-not-regex 'tags tgy' --exclude-no-imdb  -R "https://some.pt.site/torrentrss.php?rows=10&tags=gf%zz&exp=90....."  -c "c_secure_uid=ABCDE; ....c_secure_tracker_ssl=bm9wZQ=="  
```

## 注意
* 如果使用了torfilter，在获得cookie字串后，要将torfilter添加的部分删除，如这样的字串："filterParam=minimdb=5&sizerange=&titleregex=720&descregex=ç¬¬\d+&seeding=true&downloaded=false&chnsub=false&nochnlang=false"
* `--exclude-no-imdb` 选项是指站点详情页上没有提供IMDb信息即停止下载，然而大部分站点给的rss标题通过解析是可以查询到TMDb的
* `--min-imdb` 采用的是站点详情页面上给出的IMDb评分，是不可靠的，且如果页面没有给出即会导致不下载



## 定时运行
* 使用crontab定时运行rss任务
* 示例：在 `/home/ccf2013/torfilter/` 下建一个 `rss_ade.sh` 文件，内容如下：

```sh
#!/bin/bash
cd /home/ccf2013/torfilter/
python3 /home/ccf2013/torfilter/torss.py --title-not-regex 'Ep?\d+' --min-imdb 6 -R "https://adept.site/torrentrss.php?rows=10&tags=gf%zz&exp=90....."  -c "adecookie; c_secure_uid=ABCDE; ....c_secure_tracker_ssl=bm9wZQ=="  >> /home/ccf2013/log/rss_ade.log 2>&1
```

* 同目录下可再建多个，如 `rss_pter.sh`:
```sh
#!/bin/bash
cd /home/ccf2013/torfilter/
python3 /home/ccf2013/torfilter/torss.py --title-not-regex 'Ep?\d+' --min-imdb 6 --exclude-no-imdb  -R "https://pterpt.site/torrentrss.php?rows=10&tags=gf%zz&exp=90....."  -c "ptercookie; c_secure_uid=ABCDE; ....c_secure_tracker_ssl=bm9wZQ=="  >> /home/ccf2013/log/rss_pter.log 2>&1
```
* 对所建脚本加运行权限
```sh
chmod 755 /home/ccf2013/torfilter/rss_ade.sh
chmod 755 /home/ccf2013/torfilter/rss_pter.sh
```

* 运行 `crontab -e` 编辑内容如下：
```sh
0 */2 * * * /home/ccf2013/torfilter/rss_ade.sh # 每2小时运行一次，在0分开始
20 */3 * * * /home/ccf2013/torfilter/rss_pter.sh # 每3小时运行一次，在20分开始
```

* 存盘，即可