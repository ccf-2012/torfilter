from ajax_table import TorMediaItem, TorcpItemDBObj, queryByHash
from plexapi.server import PlexServer
from myconfig import CONFIG, readConfig
import argparse
import os


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
            return 

    if lib:
        lib.update(path=os.path.join(CONFIG.plexRootDir, mediaPath))
    else:
        print("Can't find the library section: " + ARGS.library)


if __name__ == '__main__':
    main()
