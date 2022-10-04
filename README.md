# torfilter

## Greasy Fork 安装地址
* https://greasyfork.org/zh-CN/scripts/451748

## 功能
油猴脚本，在种子列表页中:
1. 过滤: 未作种，无国语，有中字，标题不含，描述不含，大小介于，以及imdb大于输入值 的种子
    * 当前支持pter, chd, ade, ob, ssd
    * 大小介于的输入框中，单位为GB，使用`,`分隔。填写 `0,20` 表示小于20GB的种子
2. 新增一列快速认领，当前仅支持猫站

** 本脚本仅在打开的站点页面上进行过滤，对站点服务器无任何额外请求负担
** 在cookie中会保存参数，以便翻页时持有设置的值，不影响原cookie


## Last update:
* 2022.10.4: 加入大小介于过滤，单位GB，使用`,`分隔；
* 2022.10.4: 使用Cookie保存参数
* 2022.9.28: 标题不含，描述不含，分别搜索，忽略大小写； 加入ob, ssd支持
* 2022.9.25: 支持pter, chd, ade种子列表过滤: 过滤: 未作种， 无国语，有中字，标题不含，以及imdb大于输入值 的种子


## Note:
* Ssd 不支持国语，中字标签搜索, ssd的下载链接无passkey，无法直接用
* Ob 的下载链接无passkey，无法直接用
* PTer 个人设置中可设置是否打开预览，打开会多一列，现已都支持 credit @Aruba
