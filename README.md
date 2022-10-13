
# PT站过滤下载入库流程
![dataflow](https://ptpimg.me/lj7n0o.png)


## Last update:
* 2022.10.12: 支持Emby，支持pt站上detail页上查重和下载
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
    * 当前支持pter, chd, ade, ob, ssd
    * 大小介于的输入框中，单位为GB，使用`,` 或 `-` 分隔。填写 `0,20` 表示小于20GB的种子
2. 新增一列快速认领，当前仅支持猫站
3. since 2022.10.9，配合 dupapi.py 实现查重下载入库，请查看 https://github.com/ccf-2012/torfilter

* 本脚本仅在打开的站点页面上进行过滤，对站点服务器无任何额外请求负担
* 在cookie中会保存参数，以便翻页时持有设置的值，不影响原cookie

### 提交查重下载后，返回几种结果
* 提交下载后，页面中种子背景会改为若干种可能的颜色：
![3种结果](https://ptpimg.me/3cgnss.png)
1. 库中没有，提交qBittorrent下载了
2. 库中已有，跳过，不下载
3. TMDb没有查到，当前也是跳过不下载
4. dupapi无法提交给下载器出错时，返回400，在页面上显示红色
5. since 2022.10.12, 新增一种颜色`darkturquoise`，在种子列表页无法取得下载链接时，仅作查重而不下载


### Note:
* Ssd 不支持国语，中字标签搜索
* ob, chd, ssd的下载链接无passkey，拼合usercp中的passkey构成下载链接
* ade 的下载链接是downhash形式，无法拼合，当前没有办法批量下载
* pter, chd种子列表页面中取不到imdb id，是使用种子名称以torcp进行解析猜测。在详情页中查重和下载，会取得imdb id和下载链接，相对更可靠

-----

# 本地下载入库api服务 dupapi

![dupapi](https://ptpimg.me/16cpc0.png)

## 前置准备
1. python环境
```sh
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
* 初始化命令运行后将会退出
* sqlite 数据库存在当前目录下的 `instance` 目录中，如果想要重新初始化，可直接 `rm -rf instance` 删除再重建
* 如果以非空库运行 `--init-library` 则数据会添加并不报错
* 如果同时配置了Emby和Plex，则两个库内容都会添加


## 启动 dupapi 服务
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


