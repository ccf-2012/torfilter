from ajax_table import TorMediaItem, TorcpItemDBObj, queryByHash
import os, sys
from torcp.torcp import Torcp
from myconfig import readConfig, CONFIG
import argparse

def extractIMDbFromTag(tagstr):
    tagList = []
    if tagstr:
        tagList = tagstr.split(',')
    imdbtag = next((x for x in tagList if x.startswith('tt')), '')
    return imdbtag

def runTorcp(torpath, torhash, torsize, tortag):
    if torpath and torhash and torsize:
        npath = os.path.normpath(torpath.strip())
        torname = os.path.basename(npath)
        site_id_imdb = os.path.basename(os.path.dirname(npath))
        site = ''
        siteid = ''
        torimdb = extractIMDbFromTag(tortag)
        if "_" in site_id_imdb:
            l = site_id_imdb.split("_")
            if len(l) == 3:
                site, siteid, torimdb = l[0], l[1], l[2]
            elif len(l) == 2:
                site, siteid = l[0], l[1]

        targetDir = os.path.join(CONFIG.linkDir, torhash)
        argv = [npath, "-d", targetDir, "-s", 
                "--tmdb-api-key", CONFIG.tmdb_api_key, 
                "--tmdb-lang", CONFIG.tmdbLang, 
                "--make-log", CONFIG.bracket, 
                "-e", "srt",
                "--extract-bdmv", "--tmdb-origin-name"]
        if CONFIG.lang:
            argv += ["--lang", CONFIG.lang]
        if torimdb:
            argv += ["--imdbid", torimdb]
        print(argv)
        eo = TorcpItemDBObj(site, siteid, torimdb, torhash.strip(), int(torsize.strip()))
        o = Torcp()
        o.main(argv, eo)
        return  200
    return  401


def loadArgs():
    parser = argparse.ArgumentParser(description='wrapper to TORCP to save log in sqlite db.')
    parser.add_argument('-F', '--full-path', help='full torrent save path.')
    parser.add_argument('-I', '--info-hash', help='info hash of the torrent.')
    parser.add_argument('-G', '--tag', help='tag of the torrent.')
    parser.add_argument('-Z', '--size', help='size of the torrent.')
    parser.add_argument('-C', '--config', help='config file.')

    global ARGS
    ARGS = parser.parse_args()


def main():
    loadArgs()
    readConfig(ARGS.config)
    runTorcp(ARGS.full_path, ARGS.info_hash, ARGS.size, ARGS.tag)


if __name__ == '__main__':
    main()
