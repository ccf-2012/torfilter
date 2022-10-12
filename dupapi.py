# curl -i -H "Content-Type: application/json" -X POST -d '{"torname" : "The Frozen Ground 2013 1080p BluRay x265 10bit DTS-ADE", "imdb": "tt2005374", "downloadlink": "https://audiences.me/download.php?id=71406&...."}' http://localhost:3000/p/api/v1.0/checkdupe

from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
# from flask_httpauth import HTTPBasicAuth
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
import os
from torcp.tmdbparser import TMDbNameParser
from plexapi.server import PlexServer
from emby_client import EmbyClient
import configparser
import argparse
import qbittorrentapi


# auth = HTTPBasicAuth()

# @auth.get_password
# def get_password(username):
#     if username == 'miguel':
#         return 'python'
#     return None

# @auth.error_handler
# def unauthorized():
#     return make_response(jsonify({'error': 'Unauthorized access'}), 401)

app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medialist.db'
db = SQLAlchemy(app)
# db.init_app(app)


class configData():
    interval = 3
    plexServer = ''
    plexToken = ''
    qbServer = ''
    tmdb_api_key = ''
    qbPort = ''
    qbUser = ''
    qbPass = ''
    addPause = False
    dryrun = False


CONFIG = configData()


class MediaItem(db.Model):
    __tablename__ = 'media_list_table'
    id = db.Column(db.Integer, primary_key=True)
    # site = db.Column(db.String(64))
    title = db.Column(db.String(255))
    originalTitle = db.Column(db.String(255))
    librarySectionID = db.Column(db.String(16))
    audienceRating = db.Column(db.Float)
    guid = db.Column(db.String(64))
    key = db.Column(db.String(64))
    imdb = db.Column(db.String(32))
    tmdb = db.Column(db.String(32))
    tvdb = db.Column(db.String(32))
    doubanid = db.Column(db.String(32))
    site = db.Column(db.String(32))
    linkid = db.Column(db.String(32))
    location0 = db.Column(db.String(255))
    locationdirname = db.Column(db.String(255))

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'tmdb': self.tmdb,
        }

    def __repr__(self):
        return '<PlexItem %r>' % self.title


def validDownloadlink(downlink):
    keystr = ['passkey', 'downhash']
    return any(x in downlink for x in keystr)


@app.route('/p/api/v1.0/dupedownload', methods=['POST'])
# @auth.login_required
def checkDupAddTor():
    if not request.json or 'torname' not in request.json:
        abort(400)

    if (not CONFIG.qbServer):
        print("qBittorrent not set, skip")
        abort(400)

    if (not CONFIG.tmdb_api_key):
        print("tmdb_api_key not set, skip")
        abort(400)

    p = TMDbNameParser(CONFIG.tmdb_api_key, '')

    imdbstr = ''
    if 'imdbid' in request.json:
        imdbstr = request.json['imdbid'].strip()
    torTMDb = searchTMDb(p, request.json['torname'], imdbstr)

    if torTMDb > 0:
        # q = db.session.query(PlexItem).filter_by(tmdb=torTMDb).first()
        exists = db.session.query(db.exists().where(
            MediaItem.tmdb == torTMDb)).scalar()
        if (exists):
            return jsonify({'Dupe': True}), 202
        else:
            # print("Download: " + request.json['torname'] + "  "+request.json['downloadlink'])
            if not CONFIG.dryrun:
                if 'downloadlink' in request.json:
                    if not validDownloadlink(request.json['downloadlink']):
                        print("Not valid torrent downlink: " +
                              request.json['torname'])
                        return jsonify({'no dupe but not download': True}), 205

                    print("Added: " + request.json['torname'])
                    if not addQbitWithTag(request.json['downloadlink'].strip(), imdbstr):
                        abort(400)
            else:
                print("DRYRUN: " + request.json['torname'])

            return jsonify({'Download': True}), 201
    else:
        # if CONFIG.download_no_imdb:
        #     if not addQbitWithTag(request.json['downloadlink'].strip(), imdbstr):
        #         abort(400)
        return jsonify({'TMDbNotFound': True}), 203


@app.route('/p/api/v1.0/checkdupeonly', methods=['POST'])
# @auth.login_required
def detailCheckDupe():
    if not request.json or 'torname' not in request.json:
        abort(400)

    if (not CONFIG.qbServer):
        print("qBittorrent not set, skip")
        abort(400)

    if (not CONFIG.tmdb_api_key):
        print("tmdb_api_key not set, skip")
        abort(400)

    p = TMDbNameParser(CONFIG.tmdb_api_key, '')

    imdbstr = ''
    if 'imdbid' in request.json:
        imdbstr = request.json['imdbid'].strip()
        # print("has IMDb: " + imdbstr)
    torTMDb = searchTMDb(p, request.json['torname'], imdbstr)

    if torTMDb > 0:
        # q = db.session.query(PlexItem).filter_by(tmdb=torTMDb).first()
        exists = db.session.query(db.exists().where(
            MediaItem.tmdb == torTMDb)).scalar()
        if (exists):
            return jsonify({'Dupe': True}), 202
        else:
            return jsonify({'No Dupe': True}), 201
    else:
        # if CONFIG.download_no_imdb:
        #     if not addQbitWithTag(request.json['downloadlink'].strip(), imdbstr):
        #         abort(400)
        return jsonify({'TMDbNotFound': True}), 203


@app.route('/p/api/v1.0/delete/<int:tor_id>', methods=['DELETE'])
# @auth.login_required
def delete_torrent(tor_id):
    MediaItem.query.filter_by(tor_id).delete()
    db.session.commit()
    return jsonify({'OK': 200})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/p/api/v1.0/get/<int:tor_id>', methods=['GET'])
# @auth.login_required
def get_torrent(tor_id):
    tor = MediaItem.query.get_or_404(tor_id)

    return jsonify({'tor': tor.title})


@app.route('/p/api/v1.0/list', methods=['GET'])
# @auth.login_required
def get_torrents():
    torlist = MediaItem.query.limit(10).all()
    return jsonify(torrents=[e.serialize() for e in torlist])


@app.route('/p/api/v1.0/test', methods=['GET'])
# @auth.login_required
def test_tasks():
    datestr = '2022-03-16 05:25:53'
    thetime = datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
    return jsonify(thetime)


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
            print('Torrent added.')
        else:
            print('Torrent not added! something wrong with qb api ...')
    except Exception as e:
        print('Torrent not added! Exception: '+str(e))
        return False

    return True


def tryFloat(fstr):
    try:
        f = float(fstr)
    except:
        f = 0.0
    return f


def isMediaExt(path):
    fn, ext = os.path.splitext(path)
    return ext in ['.mkv', '.mp4', '.ts', '.m2ts']


def loadEmbyLibrary():
    if not (CONFIG.embyServer and CONFIG.embyUser):
        print("Set the EMBY section in config.ini")
        return
    print("Create Database....")
    with app.app_context():
        db.create_all()

    print("Connect to the Emby server: " + CONFIG.embyServer)
    ec = EmbyClient(CONFIG.embyServer, CONFIG.embyUser, CONFIG.embyPass)
    p = TMDbNameParser(CONFIG.tmdb_api_key, 'en')

    r = ec.getMediaList()
    for item in r:
        # print(item["Name"])
        pi = MediaItem(title=item["Name"])
        pi.key = item["ServerId"]
        pi.audienceRating = item["CommunityRating"] if "CommunityRating" in item else 0
        pi.locationdirname = os.path.basename(os.path.dirname(item["Path"]))

        guids = item["ProviderIds"]
        pi.imdb = guids['Imdb'] if 'Imdb' in guids else ''
        pi.tmdb = guids['Tmdb'] if 'Tmdb' in guids else ''
        pi.tvdb = guids['Tvdb'] if 'Tvdb' in guids else ''

        pd = item["PremiereDate"] if "PremiereDate" in item else ""
        if 'Tmdb' not in guids:
            print("No TMDb: " + item["Name"] + pd)
            pi.tmdb = searchTMDb(p, item["Name"], pi.imdb)
        with app.app_context():
            db.session.add(pi)
            db.session.commit()


# @app.route('/sitetor/api/v1.0/init', methods=['GET'])
def loadPlexLibrary():
    if not (CONFIG.plexServer and CONFIG.plexToken):
        print("Set the 'server_token' and 'server_url' in config.ini")
        return
    print("Create Database....")
    with app.app_context():
        db.create_all()

    print("Connect to the Plex server: " + CONFIG.plexServer)
    baseurl = CONFIG.plexServer  # 'http://{}:{}'.format(ip, port)
    plex = PlexServer(baseurl, CONFIG.plexToken)
    # movies = plex.library.section(sectionstr)
    p = TMDbNameParser(CONFIG.tmdb_api_key, 'en')
    for idx, video in enumerate(plex.library.all()):
        pi = MediaItem(title=video.title)
        pi.originalTitle = video.originalTitle
        pi.librarySectionID = video.librarySectionID
        pi.audienceRating = tryFloat(video.audienceRating)
        pi.guid = video.guid
        pi.key = video.key
        if len(video.locations) > 0:
            pi.location0 = video.locations[0]
            if isMediaExt(video.locations[0]):
                pi.locationdirname = os.path.basename(
                    os.path.dirname(video.locations[0]))
            else:
                pi.locationdirname = os.path.basename(video.locations[0])
        else:
            print('No location: ', video.title)
        imdb = ''
        for guid in video.guids:
            imdbmatch = re.search(r'imdb://(tt\d+)', guid.id, re.I)
            if imdbmatch:
                pi.imdb = imdbmatch[1]
                imdb = imdbmatch[1]
            tmdbmatch = re.search(r'tmdb://(\d+)', guid.id, re.I)
            if tmdbmatch:
                pi.tmdb = tmdbmatch[1]
            tvdbmatch = re.search(r'tvdb://(\d+)', guid.id, re.I)
            if tvdbmatch:
                pi.tvdb = tvdbmatch[1]
        if not pi.tmdb:
            pi.tmdb = searchTMDb(p, video.title, imdb)
        with app.app_context():
            db.session.add(pi)
            db.session.commit()
        print("%d : %s , %s , %s, %s" % (idx, video.title,
              video.originalTitle, video.locations, video.guids))


def readConfig():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # CONFIG.interval = config['PLEX'].getint('interval', 3)
    # 'http://{}:{}'.format(ip, port)
    if 'PLEX' in config:
        CONFIG.plexServer = config['PLEX'].get('server_url', '')
        # https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
        CONFIG.plexToken = config['PLEX'].get('server_token', '')

    if 'EMBY' in config:
        CONFIG.embyServer = config['EMBY'].get('server_url', '')
        CONFIG.embyUser = config['EMBY'].get('user', '')
        CONFIG.embyPass = config['EMBY'].get('pass', '')

    if 'TMDB' in config:
        CONFIG.tmdb_api_key = config['TMDB'].get('api_key', '')

    if 'QBIT' in config:
        CONFIG.qbServer = config['QBIT'].get('server_ip', '')
        CONFIG.qbPort = config['QBIT'].get('port', '')
        CONFIG.qbUser = config['QBIT'].get('user', '')
        CONFIG.qbPass = config['QBIT'].get('pass')

        CONFIG.addPause = config['QBIT'].getboolean('pause', False)
        CONFIG.dryrun = config['QBIT'].getboolean('dryrun', False)


def searchTMDb(TmdbParser, title, imdb):
    if imdb:
        TmdbParser.parse(title, TMDb=True, hasIMDb=imdb)
    else:
        TmdbParser.parse(title, TMDb=True)
    return TmdbParser.tmdbid


def fillTMDbListDb():
    with app.app_context():
        query = db.session.query(MediaItem).filter(MediaItem.tmdb == None)
        if not CONFIG.tmdb_api_key:
            print("Set the ['TMDB']['api_key'] in config.ini")
            return

        p = TMDbNameParser(CONFIG.tmdb_api_key, 'en')
        for row in query:
            row.tmdb = searchTMDb(p, row.title, row.imdb)
            # row.save()
            db.session.commit()


def loadArgs():
    global ARGS
    parser = argparse.ArgumentParser(
        description='A torrent handler does library dupe check, add qbit with tag, etc.'
    )
    parser.add_argument('--init-library', action='store_true',
                        help='init database with plex query.')
    parser.add_argument('--fill-tmdb', action='store_true',
                        help='fill tmdb field if it miss.')
    ARGS = parser.parse_args()


def main():
    loadArgs()
    readConfig()
    if ARGS.init_library:
        loadPlexLibrary()
        loadEmbyLibrary()
    elif ARGS.fill_tmdb:
        fillTMDbListDb()
    else:
        app.run(host='0.0.0.0', port=3006, debug=True)


if __name__ == '__main__':
    main()
