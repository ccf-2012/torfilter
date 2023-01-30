
import qbittorrentapi
import myconfig


def getAutoRunProgram():
    qbClient = qbittorrentapi.Client(
        host=myconfig.CONFIG.qbServer, port=myconfig.CONFIG.qbPort, username=myconfig.CONFIG.qbUser, password=myconfig.CONFIG.qbPass)

    try:
        qbClient.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        print(e)
        return False
    except:
        return False

    if not qbClient:
        return False

    prefs = qbClient.app_preferences()
    autoprog = prefs["autorun_program"]
    return autoprog



def setAutoRunProgram(prog):
    qbClient = qbittorrentapi.Client(
        host=myconfig.CONFIG.qbServer, port=myconfig.CONFIG.qbPort, username=myconfig.CONFIG.qbUser, password=myconfig.CONFIG.qbPass)

    try:
        qbClient.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        print(e)
        return False
    except:
        return False

    if not qbClient:
        return False

    qbClient.app_set_preferences(prefs={"autorun_enabled": True, "autorun_program": prog})
    return True


def addQbitWithTag(downlink, imdbtag, siteIdStr=None):
    qbClient = qbittorrentapi.Client(
        host=myconfig.CONFIG.qbServer, port=myconfig.CONFIG.qbPort, username=myconfig.CONFIG.qbUser, password=myconfig.CONFIG.qbPass)

    try:
        qbClient.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        print(e)
        return False

    if not qbClient:
        return False

    try:
        # curr_added_on = time.time()
        if siteIdStr:
            result = qbClient.torrents_add(
                urls=downlink,
                save_path=siteIdStr,
                # download_path=download_location,
                # category=timestamp,
                tags=[imdbtag],
                use_auto_torrent_management=False)
        else:
            result = qbClient.torrents_add(
                urls=downlink,
                tags=[imdbtag],
                use_auto_torrent_management=False)
        # breakpoint()
        if 'OK' in result.upper():
            pass
            # print('   >> Torrent added.')
        else:
            print('   >> Torrent not added! something wrong with qb api ...')
    except Exception as e:
        print('   >> Torrent not added! Exception: '+str(e))
        return False

    return True
