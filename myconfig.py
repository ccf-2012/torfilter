import configparser
import os

class configData():
    interval = 3
    plexServer = ''
    plexToken = ''
    plexRootDir = ''
    plexSectionList = []
    embyServer = ''
    embyUser = ''
    embyPass = ''
    qbServer = ''
    tmdb_api_key = ''
    qbPort = ''
    qbUser = ''
    qbPass = ''
    apiRunProgram = False
    dockerFrom = ''
    dockerTo = ''
    addPause = False
    dryrun = False
    linkDir = ''
    bracket = ''
    tmdbLang = 'en'
    lang = 'cn,ja,ko'
    basicAuthUser = ''
    basicAuthPass = ''
    rcpshfile = ''


CONFIG = configData()


def readConfig(cfgFile):
    config = configparser.ConfigParser()
    config.read(cfgFile)

    # CONFIG.interval = config['PLEX'].getint('interval', 3)
    # 'http://{}:{}'.format(ip, port)
    if 'AUTH' in config:
        CONFIG.basicAuthUser = config['AUTH'].get('user', '')
        CONFIG.basicAuthPass = config['AUTH'].get('pass', '')

    if 'PLEX' in config:
        CONFIG.plexServer = config['PLEX'].get('server_url', '')
        # https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
        CONFIG.plexToken = config['PLEX'].get('server_token', '')
        CONFIG.plexRootDir = config['PLEX'].get('rootdir', '')

    if 'PLEX_SECTION' in config:
        configitems = config.items('PLEX_SECTION')
        for key, value in configitems:
            if ',' in value:
                CONFIG.plexSectionList += [(key, subval.strip())
                                           for subval in value.split(',')]
            else:
                CONFIG.plexSectionList.append((key, value))
        # print(configitems)
        # CONFIG.plexSectionList = [(key, value) for key,value in configitems ]
            #   config['PLEX'].get('sectionList', '')

    if 'EMBY' in config:
        CONFIG.embyServer = config['EMBY'].get('server_url', '')
        CONFIG.embyUser = config['EMBY'].get('user', '')
        CONFIG.embyPass = config['EMBY'].get('pass', '')

    if 'TMDB' in config:
        CONFIG.tmdb_api_key = config['TMDB'].get('api_key', '')

    if 'TORCP' in config:
        CONFIG.linkDir = config['TORCP'].get('linkdir', '')
        CONFIG.bracket = config['TORCP'].get('bracket', '')
        # if not CONFIG.bracket.startswith('--'):
        #     CONFIG.bracket = '--' + CONFIG.bracket
        CONFIG.tmdbLang = config['TORCP'].get('tmdb_lang', 'en-US')
        CONFIG.lang = config['TORCP'].get('lang', 'cn,ja,ko')

    if 'QBIT' in config:
        CONFIG.qbServer = config['QBIT'].get('server_ip', '')
        CONFIG.qbPort = config['QBIT'].get('port', '')
        CONFIG.qbUser = config['QBIT'].get('user', '')
        CONFIG.qbPass = config['QBIT'].get('pass', '')

        CONFIG.apiRunProgram = config['QBIT'].get('apirun', 'False')
        CONFIG.dockerFrom = config['QBIT'].get('dockerFrom', '')
        CONFIG.dockerTo = config['QBIT'].get('dockerTo', '')

        CONFIG.addPause = config['QBIT'].getboolean('pause', False)
        CONFIG.dryrun = config['QBIT'].getboolean('dryrun', False)

        CONFIG.rcpshfile = os.path.join(os.getcwd(), 'rcp.sh')


def generatePassword(cfgFile):
    config = configparser.ConfigParser()
    config.read(cfgFile)
    # https://stackoverflow.com/questions/3854692/generate-password-in-python
    import secrets
    CONFIG.basicAuthUser = 'admin'
    CONFIG.basicAuthPass = secrets.token_urlsafe(12)
    if not config.has_section('AUTH'):
        config.add_section('AUTH')
    config.set('AUTH', 'user', CONFIG.basicAuthUser)
    config.set('AUTH', 'pass', CONFIG.basicAuthPass)

    print('config file: %s' % cfgFile)
    print("username: %s \npassword: %s" %
          (CONFIG.basicAuthUser, CONFIG.basicAuthPass))
    with open(cfgFile, 'w') as f:
        config.write(f)


def updateConfigSettings(cfgFile, linkDir, bracket, tmdbLang, lang, tmdb_api_key):
    config = configparser.ConfigParser()
    config.read(cfgFile)
    if not config.has_section('TORCP'):
        config.add_section('TORCP')
    config.set('TORCP', 'linkdir', linkDir)
    config.set('TORCP', 'bracket', bracket)
    config.set('TORCP', 'tmdb_lang', tmdbLang)
    config.set('TORCP', 'lang', lang)
    if not config.has_section('TMDB'):
        config.add_section('TMDB')
    config.set('TMDB', 'api_key', tmdb_api_key)
    with open(cfgFile, 'w') as f:
        config.write(f)

    CONFIG.linkDir = config['TORCP'].get('linkdir', '')
    CONFIG.bracket = config['TORCP'].get('bracket', '')
    CONFIG.tmdbLang = config['TORCP'].get('tmdb_lang', 'en-US')
    CONFIG.lang = config['TORCP'].get('lang', 'cn,ja,ko')
    CONFIG.tmdb_api_key = config['TMDB'].get('api_key', '')


def updateQBSettings(cfgFile, qbhost, qbport, qbuser, qbpass, qbapirun, dockerFrom, dockerTo):
    config = configparser.ConfigParser()
    config.read(cfgFile)
    if not config.has_section('QBIT'):
        config.add_section('QBIT')
    config.set('QBIT', 'server_ip', qbhost)
    config.set('QBIT', 'port', qbport)
    config.set('QBIT', 'user', qbuser)
    config.set('QBIT', 'pass', qbpass)
    config.set('QBIT', 'apirun', qbapirun)
    config.set('QBIT', 'dockerFrom', dockerFrom)
    config.set('QBIT', 'dockerTo', dockerTo)
    with open(cfgFile, 'w') as f:
        config.write(f)

    CONFIG.qbServer = config['QBIT'].get('server_ip', '')
    CONFIG.qbPort = config['QBIT'].get('port', '')
    CONFIG.qbUser = config['QBIT'].get('user', '')
    CONFIG.qbPass = config['QBIT'].get('pass', '')
    CONFIG.apiRunProgram = config['QBIT'].get('apirun', 'False')
    CONFIG.dockerFrom = config['QBIT'].get('dockerFrom', '')
    CONFIG.dockerTo = config['QBIT'].get('dockerTo', '')

