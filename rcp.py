from cplist import TorMediaItem, TorcpItemDBObj, queryByHash
import os
from torcp.torcp import Torcp
from myconfig import readConfig, CONFIG
import argparse
import re


def extractIMDbFromTag(tagstr):
    tagList = []
    if tagstr:
        tagList = tagstr.split(',')
    imdbtag = next((x for x in tagList if x.startswith('tt')), '')
    return imdbtag


def parseSiteId(siteidStr, torimdb):
    site = ''
    siteid = ''
    m = re.search(r'(\w+)[_-](\d+)(_(tt\d+))?', siteidStr, re.I)
    if m:
        site = m[1]
        siteid = m[2]
        if not torimdb and m[4]:
            torimdb = m[4]
    return site, siteid, torimdb


def tryint(instr):
    try:
        string_int = int(instr)
    except ValueError:
        string_int = 0
    return string_int


def  getSiteIdDirName(pathStr, savepath):
    npath = os.path.normpath(pathStr.strip())
    siteIdFolder = os.path.basename(os.path.normpath(savepath))
    relativePath = os.path.relpath(npath, savepath)
    l = relativePath.split(os.path.sep)
    torRootFolder = os.path.join(savepath, l[0]) if len(l) > 0 else npath
    return torRootFolder, siteIdFolder
        

def runTorcp(torpath, torhash, torsize, tortag, savepath, insertHashDir):
    print("torpath: %s, torhash: %s, torsize: %s, tortag: %s, savepath: %s" % (torpath, torhash, torsize, tortag, savepath))
    if torpath and torhash and torsize:
        torimdb = extractIMDbFromTag(tortag)
        rootdir, site_id_imdb = getSiteIdDirName(torpath, savepath)

        site, siteid, torimdb = parseSiteId(site_id_imdb, torimdb)
        if insertHashDir:
            targetDir = os.path.join(CONFIG.linkDir, torhash)
        else:
            targetDir = CONFIG.linkDir
        argv = [rootdir, "-d", targetDir, "-s",
                "--tmdb-api-key", CONFIG.tmdb_api_key,
                "--tmdb-lang", CONFIG.tmdbLang,
                "--make-log", 
                CONFIG.bracket,
                "-e", "srt",
                "--extract-bdmv", 
                "--tmdb-origin-name"]
        if CONFIG.lang:
            argv += ["--lang", CONFIG.lang]
        if torimdb:
            argv += ["--imdbid", torimdb]
        print(argv)
        eo = TorcpItemDBObj(site, siteid, torimdb,
                            torhash.strip(), tryint(torsize.strip()))
        o = Torcp()
        o.main(argv, eo)
        return 200
    return 401



def loadArgs():
    parser = argparse.ArgumentParser(
        description='wrapper to TORCP to save log in sqlite db.')
    parser.add_argument('-F', '--full-path', help='full torrent save path.')
    parser.add_argument('-I', '--info-hash', help='info hash of the torrent.')
    parser.add_argument('-D', '--save-path', help='qbittorrent save path.')
    parser.add_argument('-G', '--tag', help='tag of the torrent.')
    parser.add_argument('-Z', '--size', help='size of the torrent.')
    parser.add_argument('-C', '--config', help='config file.')

    global ARGS
    ARGS = parser.parse_args()
    if not ARGS.config:
        ARGS.config = os.path.join(os.getcwd(), 'config.ini')

    
def main():
    loadArgs()
    readConfig(ARGS.config)
    runTorcp(ARGS.full_path, ARGS.info_hash, ARGS.size, ARGS.tag, ARGS.save_path, insertHashDir=True)


if __name__ == '__main__':
    main()
