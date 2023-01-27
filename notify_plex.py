from ajax_table import TorMediaItem, TorcpItemDBObj, queryByHash
from plexapi.server import PlexServer
from myconfig import CONFIG, readConfig
import argparse
import os
import time


MAX_RETRY = 5

def main():
    parser = argparse.ArgumentParser(description='Notify plex server to add a file/folder.')
    parser.add_argument('-I', '--info-hash', type=str, required=True, help='info hash of the torrent.')
    parser.add_argument('-C', '--config', help='config file.')

    ARGS = parser.parse_args()
    readConfig(ARGS.config)
    plexSrv = PlexServer(CONFIG.plexServer, CONFIG.plexToken)
    mediaItem = queryByHash(ARGS.info_hash)

    if mediaItem and plexSrv:
        mediaPath = mediaItem.location.strip()
        if mediaPath.startswith('TV/cn'):
            lib = plexSrv.library.section('中文剧集')
        elif mediaPath.startswith('TV/ja'):
            lib = plexSrv.library.section('日韩剧集')
        elif mediaPath.startswith('TV/ko'):
            lib = plexSrv.library.section('日韩剧集')
        elif mediaPath.startswith('TV/other'):
            lib = plexSrv.library.section('剧集')
        elif mediaPath.startswith('Movie/cn'):
            lib = plexSrv.library.section('中文电影')
        elif mediaPath.startswith('Movie'):
            lib = plexSrv.library.section('电影')
        else:
            print("Can't match any library: " + mediaPath)
            return 

        if lib:
            for n in range(MAX_RETRY):
                try:    
                    lib.update(path=os.path.join(CONFIG.plexRootDir, mediaPath))
                    break
                except Exception as e:
                    if n < MAX_RETRY:
                        print('Fail: lib.update' + str(e))
                        print('retry %d time.' % (n+1))
                        time.sleep(3)
                    else:
                        print('Error: MAX_RETRY(%d) times' % (MAX_RETRY))
                        os._exit(1)
                
        else:
            print("Can't find the library section: " + ARGS.library)
    else:
        print("Info hash not found/Plex server not connected. ")


if __name__ == '__main__':
    main()
