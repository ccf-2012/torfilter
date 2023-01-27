from ajax_table import TorMediaItem, TorcpItemDBObj, queryByHash
from plexapi.server import PlexServer
from myconfig import CONFIG
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description='Notify plex server to add a file/folder.')
    parser.add_argument('-I', '--info-hash', type=str, required=True, help='info hash of the torrent.')

    ARGS = parser.parse_args()

    plexSrv = PlexServer(CONFIG.plexServer, CONFIG.plexToken)
    mediaItem = queryByHash(ARGS.info_hash)

    if mediaItem and plexSrv:
        mediaPath = mediaItem.location
        if mediaPath.startwith('TV/cn'):
            lib = plexSrv.library.section('中文剧集')
        elif mediaPath.startwith('TV/ja'):
            lib = plexSrv.library.section('日韩剧集')
        elif mediaPath.startwith('TV/ko'):
            lib = plexSrv.library.section('日韩剧集')
        elif mediaPath.startwith('TV/other'):
            lib = plexSrv.library.section('剧集')
        elif mediaPath.startwith('Movie/cn'):
            lib = plexSrv.library.section('中文电影')
        elif mediaPath.startwith('Movie'):
            lib = plexSrv.library.section('电影')
        else:
            return 

    if lib:
        lib.update(path=os.path.join(CONFIG.plexRootDir, mediaPath))
    else:
        print("Can't find the library section: " + ARGS.library)


if __name__ == '__main__':
    main()
