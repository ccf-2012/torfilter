import configparser

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
    linkDir = ''
    bracket = ''
    tmdbLang = 'en'
    lang = 'cn,ja,ko'

global CONFIG
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

    if 'TORCP' in config:
        CONFIG.linkDir = config['TORCP'].get('linkdir', '')
        CONFIG.bracket = config['TORCP'].get('bracket', '')
        CONFIG.tmdbLang = config['TORCP'].get('tmdb_lang', 'en')
        if not CONFIG.tmdbLang.startswith('--'):
            CONFIG.tmdbLang = '--' + CONFIG.tmdbLang
        CONFIG.lang = config['TORCP'].get('lang', 'cn,ja,ko')

    if 'QBIT' in config:
        CONFIG.qbServer = config['QBIT'].get('server_ip', '')
        CONFIG.qbPort = config['QBIT'].get('port', '')
        CONFIG.qbUser = config['QBIT'].get('user', '')
        CONFIG.qbPass = config['QBIT'].get('pass')

        CONFIG.addPause = config['QBIT'].getboolean('pause', False)
        CONFIG.dryrun = config['QBIT'].getboolean('dryrun', False)

readConfig()
