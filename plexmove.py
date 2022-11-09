from emby_client import EmbyClient
from plexapi.server import PlexServer
import configparser
import argparse

class configData():
    interval = 3
    plexServer = ''
    plexToken = ''
    embyServer = ''
    embyUser = ''
    embyPass = ''
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



def loadArgs():
    global ARGS
    parser = argparse.ArgumentParser(
        description='A torrent handler does library dupe check, add qbit with tag, etc.'
    )
    parser.add_argument('--plex-move', action='store_true',
                        help='init database with plex query.')
    parser.add_argument('--emby-move', action='store_true',
                        help='init database with plex query.')
    ARGS = parser.parse_args()


def movePlexLibrary():
    if not (CONFIG.plexServer and CONFIG.plexToken):
        print("Set the 'server_token' and 'server_url' in config.ini")
        return

    sectionstr = '剧集'
    print("Connect to the Plex server: " + CONFIG.plexServer)
    baseurl = CONFIG.plexServer  # 'http://{}:{}'.format(ip, port)
    plex = PlexServer(baseurl, CONFIG.plexToken)
    medias = plex.library.section(sectionstr)
    # for idx, video in enumerate(plex.library.all()):
    docuCount = 0
    for idx, video in enumerate(medias.all()):
        # gtags = [g for g in video.genres if g.tag == '纪录']
        hasDocu = next((g for g in video.genres if g.tag == '纪录'), None)
        if hasDocu:
            docuCount += 1
            print(str(docuCount) + '  ' + video.title)
                # for g in video.genres:
                #     print(" >>" + g.tag)
            if len(video.locations) > 0:
                print(video.locations[0])
            else:
                print('\033[33mNo location: %s \033[0m' % video.title)


def main():
    loadArgs()
    readConfig()
    # if ARGS.plex_move:
    movePlexLibrary()


if __name__ == '__main__':
    main()



