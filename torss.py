# -*- coding: utf-8 -*-
"""
A script to rss and parse the info page of a torrent to get IMDb id, 
add torrent to the qbit client with this IMDb id as a tag.
"""
import re
import argparse
import requests
from http.cookies import SimpleCookie
from torcp.tmdbparser import TMDbNameParser
import qbittorrentapi
import configparser
import feedparser
import datetime
import time
from sqlalchemy import Column, String, Integer, Float, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


from humanbytes import HumanBytes
# from lxml import etree

DOWNLOAD_URL_RE = [
    r'https?://(\w+\.)?\w+\.\w+/download\.php\?id=(\d+)&downhash=(\w+)',
    r'https?://(\w+\.)?\w+\.\w+/download\.php\?id=(\d+)&passkey=(\w+)',
]


class configData():
    interval = 3
    qbServer = ''
    tmdb_api_key = ''
    qbPort = ''
    qbUser = ''
    qbPass = ''
    addPause = False
    dryrun = False


CONFIG = configData()


def readConfig():
    config = configparser.ConfigParser()
    config.read('config.ini')

    if 'TMDB' in config:
        CONFIG.tmdb_api_key = config['TMDB'].get('api_key', '')

    if 'QBIT' in config:
        CONFIG.qbServer = config['QBIT'].get('server_ip', '')
        CONFIG.qbPort = config['QBIT'].get('port', '')
        CONFIG.qbUser = config['QBIT'].get('user', '')
        CONFIG.qbPass = config['QBIT'].get('pass')

        CONFIG.addPause = config['QBIT'].getboolean('pause', False)
        CONFIG.dryrun = config['QBIT'].getboolean('dryrun', False)


ModelBase = declarative_base()


class MediaItem(ModelBase):
    __tablename__ = 'media_list_table'
    id = Column(Integer, primary_key=True)
    # site = Column(String(64))
    title = Column(String(255))
    originalTitle = Column(String(255))
    librarySectionID = Column(String(16))
    audienceRating = Column(Float)
    guid = Column(String(64))
    key = Column(String(64))
    imdb = Column(String(32))
    tmdb = Column(String(32))
    tvdb = Column(String(32))
    doubanid = Column(String(32))
    site = Column(String(32))
    linkid = Column(String(32))
    location0 = Column(String(255))
    locationdirname = Column(String(255))

    def __repr__(self):
        return '<PlexItem %r>' % self.title


class RSSHistory(ModelBase):
    __tablename__ = 'rss_history_table'
    id = Column(Integer, primary_key=True)
    # site = Column(String(64))
    title = Column(String(255))
    # imdbstr = Column(String(32))


# 初始化数据库连接:
engine = create_engine('sqlite:///instance/medialist.db')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
SESSION = DBSession()
ModelBase.metadata.create_all(engine)


def rssGetDetailAndDownload(rsslink):
    feed = feedparser.parse(rsslink)
    rssSum = 0
    rssAccept = 0
    for item in feed.entries:
        if not hasattr(item, 'id'):
            print('!! No id')
            continue
        if not hasattr(item, 'title'):
            print('!! No title')
            continue

        if existsRssHistory(item.title):
            # print("   >> exists in rss history, skip")
            continue

        rssSum += 1
        print("%d: %s (%s)" % (rssSum, item.title,
              datetime.datetime.now().strftime("%H:%M:%S")))

        saveRssHistory(item.title)

        if ARGS.title_regex:
            if not re.search(ARGS.title_regex, item.title, re.I):
                print('  >> title_regex not match.')
                continue

        if ARGS.title_not_regex:
            if re.search(ARGS.title_not_regex, item.title, re.I):
                print('  >> title_not_regex not match.')
                continue

        imdbstr = ''
        if ARGS.cookie:
            if hasattr(item, 'link'):
                match, imdbstr, downlink = parseDetailPage(
                    item.link, ARGS.cookie)
                if not match:
                    # print('  >> Info page regex not match.')
                    continue
                if ARGS.exclude_no_imdb and (not imdbstr):
                    print('  >> Without IMDb')
                    continue

        if hasattr(item, 'links') and len(item.links) > 1:
            rssDownloadLink = item.links[1]['href']
            rssSize = item.links[1]['length']
            # Download
            rssAccept += 1
            print('   %s (%s), %s' %
                  (imdbstr, HumanBytes.format(int(rssSize)), rssDownloadLink))
            r = checkDupAddTor(item.title, rssDownloadLink,
                               imdbstr, forceDownload=False)
            print('   >> %d ' % r)
            # if ARGS.host and ARGS.username:
            #     r = addQbitWithTag(rssDownloadLink, imdbstr)
        # print('Sleeping for %d seconds' % ARGS.sleep)
        time.sleep(ARGS.sleep)

    print('Total: %d, Accepted: %d (%s)' % (rssSum, rssAccept, datetime.datetime.now().strftime("%H:%M:%S")))


def validDownloadlink(downlink):
    keystr = ['passkey', 'downhash', 'totheglory.im/dl/', 'download.php?hash=']
    return any(x in downlink for x in keystr)


def searchTMDb(TmdbParser, title, imdb):
    if imdb:
        TmdbParser.parse(title, useTMDb=True, hasIMDbId=imdb)
    else:
        TmdbParser.parse(title, useTMDb=True)
    return TmdbParser.tmdbid


def existsRssHistory(torname):
    q = SESSION.query(RSSHistory.id).filter(RSSHistory.title == torname)
    exists = SESSION.query(q.exists()).scalar()
    return exists


def saveRssHistory(torname):
    SESSION.add(RSSHistory(title=torname))
    SESSION.commit()


def checkDatabaseExists(torTMDb):
    q = SESSION.query(MediaItem.id).filter(MediaItem.tmdb == torTMDb)
    exists = SESSION.query(q.exists()).scalar()
    return exists


def checkDupAddTor(torname, downloadLink, imdbstr, forceDownload=False):
    if not torname:
        return 400

    if (not CONFIG.qbServer):
        print("qBittorrent not set, skip")
        return 400

    if (not CONFIG.tmdb_api_key):
        print("tmdb_api_key not set, skip")
        return 400

    p = TMDbNameParser(CONFIG.tmdb_api_key, '')

    torTMDb = searchTMDb(p, torname, imdbstr)

    if torTMDb > 0:
        exists = checkDatabaseExists(torTMDb)
        # exists = session.query(exists().where(
        #     MediaItem.tmdb == torTMDb)).scalar()
        if (exists) and (not forceDownload):
            return 202
        else:
            # print("Download: " + request.json['torname'] + "  "+request.json['downloadlink'])
            if downloadLink:
                if not validDownloadlink(downloadLink):
                    print("   >> Not valid torrent downlink: %s ( %s) " %
                          (torname, downloadLink))
                    return 205

                if not CONFIG.dryrun:
                    print("   >> Added: " + torname)
                    if not addQbitWithTag(downloadLink.strip(), imdbstr):
                        return 400
                else:
                    print("   >> DRYRUN: " + torname + "\n   >> " + downloadLink)

            return 201
    else:
        # if CONFIG.download_no_imdb:
        #     if not addQbitWithTag(request.json['downloadlink'].strip(), imdbstr):
        #         abort(400)
        return 203


def addQbitWithTag(downlink, imdbtag):
    qbClient = qbittorrentapi.Client(
        host=CONFIG.qbServer, port=CONFIG.qbPort, username=CONFIG.qbUser, password=CONFIG.qbPass)

    try:
        qbClient.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        print(e)

    if not qbClient:
        return False

    try:
        # curr_added_on = time.time()
        result = qbClient.torrents_add(
            urls=downlink,
            is_paused=CONFIG.addPause,
            # save_path=download_location,
            # download_path=download_location,
            # category=timestamp,
            tags=[imdbtag],
            use_auto_torrent_management=False)
        # breakpoint()
        if 'OK' in result.upper():
            print('   >> Torrent added.')
        else:
            print('   >> Torrent not added! something wrong with qb api ...')
    except Exception as e:
        print('   >> Torrent not added! Exception: '+str(e))
        return False

    return True


# def findConfig(infoUrl):
#     hostnameList = urllib.parse.urlparse(infoUrl).netloc.split('.')
#     abbrev = hostnameList[-2] if len(hostnameList) >= 2 else ''
#     return next(filter(lambda ele: ele['host'] == abbrev, SITE_CONFIGS), None)

def tryFloat(fstr):
    try:
        f = float(fstr)
    except:
        f = 0.0
    return f


def parseDetailPage(pageUrl, pageCookie):
    cookie = SimpleCookie()
    cookie.load(pageCookie)
    cookies = {k: v.value for k, v in cookie.items()}
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    doc = requests.get(pageUrl, headers=headers, cookies=cookies).text

    if ARGS.info_regex:
        if not re.search(ARGS.info_regex, doc, flags=re.A):
            print('  >> info_regex not match.')
            return False, '', ''
    if ARGS.info_not_regex:
        if re.search(ARGS.info_not_regex, doc, flags=re.A):
            print('  >> info_not_regex not match.')
            return False, '', ''
    if ARGS.min_imdb:
        imdbval = 0
        m1 = re.search(r'IMDb评分.*?([0-9.]+)/10', doc, flags=re.A)
        if m1:
            imdbval = tryFloat(m1[1])
        doubanval = 0
        m2 = re.search(r'豆瓣评分.*?([0-9.]+)/10', doc, flags=re.A)
        if m2:
            doubanval = tryFloat(m2[1])
        print("   >> IMDb: %s, douban: %s" % (imdbval, doubanval))

        if (imdbval and imdbval < ARGS.min_imdb) and (doubanval and doubanval < ARGS.min_imdb):
            return False, '', ''


    imdbstr = ''
    # imdbRe = r'IMDb(链接)\s*(\<.[!>]*\>)?.*https://www\.imdb\.com/title/tt(\d+)'
    imdbRe = r'www\.imdb\.com\/title\/(tt\d+)'
    m1 = re.search(imdbRe, doc, flags=re.A)
    if m1:
        imdbstr = m1[1]

    for reUrl in DOWNLOAD_URL_RE:
        if re.search(reUrl, doc, flags=re.A):
            break
    downlink = ''
    m2 = re.search(reUrl, doc, flags=re.A)
    if m2:
        downlink = m2[0]

    return True, imdbstr, downlink


def loadArgs():
    parser = argparse.ArgumentParser(
        description='A script to rss pt site, add torrent to qbit with IMDb id as a tag.'
    )
    parser.add_argument('-R', '--rss', help='the rss link.')
    parser.add_argument(
        '-s', '--single', help='fetch single torrent in detail page.')
    parser.add_argument(
        '-c', '--cookie', help='the cookie to the detail page.')
    parser.add_argument('--title-regex', help='regex to match the rss title.')
    parser.add_argument('--title-not-regex', help='regex to not match the rss title.')
    parser.add_argument(
        '--info-regex', help='regex to match the info/detail page.')
    parser.add_argument('--info-not-regex',
                        help='regex to not match the info/detail page.')
    parser.add_argument('--sleep', type=int,
                        help='sleep between each request of info page.')
    parser.add_argument('--add-pause',
                        action='store_true',
                        help='Add torrent in PAUSE state.')
    parser.add_argument('--exclude-no-imdb',
                        action='store_true',
                        help='Do not download without IMDb')
    parser.add_argument('--min-imdb', type=int,
                        help='filter imdb greater than <MIN_IMDb>.')
    parser.add_argument('--init-rss-history', action='store_true',
                        help='Init rss history table.')
    global ARGS
    ARGS = parser.parse_args()
    if not ARGS.sleep:
        ARGS.sleep = 5


def initRssHistory():
    print("Init Database....")
    num_rows_deleted = SESSION.query(RSSHistory).delete()
    SESSION.commit()
    print("%d rows deleted" % num_rows_deleted)
    return num_rows_deleted


def main():
    loadArgs()
    readConfig()
    if ARGS.init_rss_history:
        initRssHistory()
    if ARGS.rss:
        rssGetDetailAndDownload(ARGS.rss)

    elif ARGS.single:
        if ARGS.cookie:
            imdbstr, downlink = parseDetailPage(ARGS.info_url, ARGS.cookie)
            if not downlink:
                print("Error: download link not found")
                return
            print(imdbstr, downlink)
            r = addQbitWithTag(downlink, imdbstr)


if __name__ == '__main__':
    main()
