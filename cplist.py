# curl -i -H "Content-Type: application/json" -X POST -d '{"torpath" : "~/torccf/frds_10018_tt6710716/真探S03.2019.1080p.WEB-DL.x265.AC3￡cXcY@FRDS", "torhash": "289256b0918c3dccea51a194a3e834664b17eafd", "torsize": "11534336"}' http://localhost:5000/api/torcp

from flask import Flask, render_template, jsonify
from flask import request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sys
import os
from torcp.torcp import Torcp
import logging
from flask_httpauth import HTTPBasicAuth
import myconfig
import argparse
from wtforms import Form, StringField, RadioField, SubmitField
from wtforms.validators import DataRequired
import qbfunc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mykey'
db = SQLAlchemy(app)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
auth = HTTPBasicAuth()


def genSiteLink(siteAbbrev, siteid, sitecat=''):
    SITE_URL_PREFIX = {
        'pter': 'https://pterclub.com/details.php?id=',
        'aud': 'https://audiences.me/details.php?id=',
        'chd': 'https://chdbits.co/details.php?id=',
        'lhd': 'https://lemonhd.org/',
        'hds': 'https://hdsky.me/details.php?id=',
        'ob': 'https://ourbits.club/details.php?id=',
        'ssd': 'https://springsunday.net/details.php?id=',
        'frds': 'https://pt.keepfrds.com/details.php?id=',
        'hh': 'https://hhanclub.top/details.php?id=',
        'ttg': 'https://totheglory.im/t/',
    }
    detailUrl = ''
    if siteAbbrev in SITE_URL_PREFIX:
        if siteAbbrev == 'lhd':
            if sitecat == 'movie':
                detailUrl = SITE_URL_PREFIX[siteAbbrev] + \
                    'details_movie.php?id=' + str(siteid)
            elif sitecat == 'tvseries':
                detailUrl = SITE_URL_PREFIX[siteAbbrev] + \
                    'details_tv.php?id=' + str(siteid)
        else:
            detailUrl = SITE_URL_PREFIX[siteAbbrev] + str(siteid)
    return detailUrl if detailUrl else '#'


class TorMediaItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    addedon = db.Column(db.DateTime, default=datetime.now)
    torname = db.Column(db.String(256), index=True)
    torsite = db.Column(db.String(64))
    torsiteid = db.Column(db.Integer)
    torsitecat = db.Column(db.String(20))
    torimdb = db.Column(db.String(20), index=True)
    torhash = db.Column(db.String(120))
    torsize = db.Column(db.Integer)
    tmdbid = db.Column(db.String(120))
    tmdbcat = db.Column(db.String(20))
    location = db.Column(db.String(256))
    plexid = db.Column(db.String(120))

    def to_dict(self):
        return {
            'torname': self.torname,
            'addedon': self.addedon,
            'torabbrev': self.torsite,
            'torsite': genSiteLink(self.torsite, self.torsiteid),
            'torsitecat': self.torsitecat,
            'torimdb': self.torimdb,
            'tmdbid': str(self.tmdbid),
            'tmdbcat': self.tmdbcat,
            'location': self.location,
        }


with app.app_context():
    db.create_all()


class TorcpItemDBObj:
    def __init__(self, torsite, torsiteid, torimdb, torhash, torsize):
        self.torsite = torsite
        self.torsiteid = torsiteid
        self.torimdb = torimdb
        self.torhash = torhash
        self.torsize = torsize

    def onOneItemTorcped(self, targetDir, mediaName, tmdbIdStr, tmdbCat):
        # print(targetDir, mediaName, tmdbIdStr, tmdbCat)
        t = TorMediaItem(torname=mediaName,
                         torsite=self.torsite,
                         torsiteid=self.torsiteid,
                         torimdb=self.torimdb,
                         torhash=self.torhash,
                         torsize=self.torsize,
                         tmdbid=tmdbIdStr,
                         tmdbcat=tmdbCat,
                         location=targetDir)
        with app.app_context():
            db.session.add(t)
            db.session.commit()


def queryByHash(qbhash):
    with app.app_context():
        query = db.session.query(TorMediaItem).filter(
            TorMediaItem.torhash == qbhash).first()
        return query


@auth.verify_password
def verify_password(username, password):
    if username == myconfig.CONFIG.basicAuthUser and password == myconfig.CONFIG.basicAuthPass:
        return username


@app.route('/')
@auth.login_required
def index():
    return render_template('ajax_table.html', title='torcp list')


class QBSettingForm(Form):
    qbhost = StringField('qBit 主机IP', validators=[DataRequired()])
    qbport = StringField('qBit 端口')
    qbuser = StringField('qBit 用户名', validators=[DataRequired()])
    qbpass = StringField('qBit 密码', validators=[DataRequired()])
    submit = SubmitField("保存设置")
    qbapirun = RadioField('qBit 如何运行外部程序', choices=[
                            (True, '通过 API 执行，适用于以docker方式安装的qBit'), 
                            (False, '以rcp.sh脚本运行')])
    dockerFrom = StringField('如果以docker安装，则将内部的路径映射出来')
    dockerTo = StringField('映射出的路径')

@app.route('/qbsetting', methods=['POST', 'GET'])
@auth.login_required
def qbitSetting():
    form = QBSettingForm()
    form.qbhost.data = myconfig.CONFIG.qbServer
    form.qbport.data = myconfig.CONFIG.qbPort
    form.qbuser.data = myconfig.CONFIG.qbUser
    form.qbpass.data = myconfig.CONFIG.qbPass
    form.qbapirun.data = myconfig.CONFIG.apiRunProgram
    form.dockerFrom.data = myconfig.CONFIG.dockerFrom
    form.dockerTo.data = myconfig.CONFIG.dockerTo
    msg = ''
    if request.method == 'POST':
        form = QBSettingForm(request.form)
        myconfig.updateQBSettings(ARGS.config,
                                form.qbhost.data,
                                form.qbport.data,
                                form.qbuser.data,
                                form.qbpass.data,
                                form.qbapirun.data,
                                form.dockerFrom.data,
                                form.dockerTo.data,
                                )
        if form.qbapirun.data == 'True':
            authstr = ' --user %s:%s ' % (myconfig.CONFIG.basicAuthUser, myconfig.CONFIG.basicAuthPass)
            apiurl = 'http://%s:5006/api/torcp' % (form.qbhost.data)
            postjson = '\'{"torpath" : "%F", "torhash": "%I", "torsize": "%Z", "savepath" : "%D", "tortag": "G"}\''
            progstr = 'curl -i' + authstr + '-H "Content-Type: application/json" -X POST -d %s %s' % (postjson, apiurl)
        else:
            progstr = os.path.join(os.getcwd(),"rcp.sh") +' "%F" "%I" "%Z" "%D" "%G" '
        r = qbfunc.setAutoRunProgram(progstr)
        if r:
            msg = 'success'
        else:
            msg = 'failed'
    return render_template('qbsetting.html', form=form, msg=msg)



class SettingForm(Form):
    linkdir = StringField('生成目标目录的存储位置', validators=[DataRequired()])
    tmdb_key = StringField('TMDb API key', validators=[DataRequired()])
    bracket = RadioField('使用括号后缀来向 Emby/Plex 指定媒体的TMDb id', choices=[
                            ('--emby-bracket', 'Emby后缀，如 [tmdbid=12345]'), 
                            ('--plex-bracket', 'Plex后缀，如{tmdb-12345}'), 
                            ('', '无后缀')])
    tmdb_lang = RadioField('TMDb 语言，生成英文或是中文目录名？', choices=[
                            ('en-US', 'en-US'), 
                            ('zh-CN', 'zh-CN')])
    sep_lang = StringField('分语言目录，以逗号分隔，将不同语言的媒体分别存在不同目录中')
    submit = SubmitField("保存设置")


@app.route('/setting', methods=['POST', 'GET'])
@auth.login_required
def setting():
    form = SettingForm()
    form.linkdir.data = myconfig.CONFIG.linkDir
    form.tmdb_key.data = myconfig.CONFIG.tmdb_api_key
    form.bracket.data = myconfig.CONFIG.bracket
    form.tmdb_lang.data = myconfig.CONFIG.tmdbLang
    form.sep_lang.data = myconfig.CONFIG.lang
    msg = ''
    if request.method == 'POST':
        form = SettingForm(request.form)
        myconfig.updateConfigSettings(ARGS.config,
                                      linkDir=form.linkdir.data,
                                      bracket=form.bracket.data,
                                      tmdbLang=form.tmdb_lang.data,
                                      lang=form.sep_lang.data,
                                      tmdb_api_key=form.tmdb_key.data)
        msg = 'success'

    return render_template('settings2.html', form=form, msg=msg)


@app.route('/editrcp', methods=['POST', 'GET'])
@auth.login_required
def editrcp():
    fn = myconfig.CONFIG.rcpshfile
    if os.path.isfile(fn):
        with open(fn, 'r') as f:
            rcpsh_file = f.read()
    msg = ''
    if request.method == 'POST':
        rcpsh_file = request.form['config_file']
        with open(fn, 'w') as f:
            f.write(str(rcpsh_file))
        msg = "Success"
        
    return render_template('editrcp.html', config_file=rcpsh_file, msg=msg)


@app.route('/api/data')
@auth.login_required
def data():
    query = TorMediaItem.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            TorMediaItem.torname.like(f'%{search}%'),
            TorMediaItem.location.like(f'%{search}%')
        ))
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['torname', 'torsite', 'addedon', 'torsize']:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(TorMediaItem, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [user.to_dict() for user in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': TorMediaItem.query.count(),
        'draw': request.args.get('draw', type=int),
    }


@app.route('/api/torcp', methods=['POST'])
@auth.login_required
def runTorcp():
    if 'torpath' in request.json and 'torhash' in request.json and 'torsize' in request.json:
        torpath = request.json['torpath'].strip()
        torhash = request.json['torhash'].strip()
        torsize = request.json['torsize'].strip()
        tortag = request.json['tortag'].strip() if 'tortag' in request.json else ''
        savepath = request.json['savepath'].strip() if 'savepath' in request.json else ''
        if myconfig.CONFIG.dockerFrom != myconfig.CONFIG.dockerTo:
            if torpath.startswith(myconfig.CONFIG.dockerFrom) and savepath.startswith(myconfig.CONFIG.dockerFrom):
                torpath = torpath.replace(myconfig.CONFIG.dockerFrom, myconfig.CONFIG.dockerTo, 1)
                savepath = savepath.replace(myconfig.CONFIG.dockerFrom, myconfig.CONFIG.dockerTo, 1)

        import rcp
        r = rcp.runTorcp(torpath, torhash, torsize, tortag, savepath)
        if r == 200:
            return jsonify({'OK': 200}), 200
    return jsonify({'Error': 401}), 401


def loadArgs():
    parser = argparse.ArgumentParser(
        description='TORCP web ui.')
    parser.add_argument('-C', '--config', help='config file.')
    parser.add_argument('-G', '--init-password',
                        action='store_true', help='init pasword.')

    global ARGS
    ARGS = parser.parse_args()
    if not ARGS.config:
        ARGS.config = os.path.join(os.getcwd(), 'config.ini')


def main():
    loadArgs()
    myconfig.readConfig(ARGS.config)
    if ARGS.init_password:
        myconfig.generatePassword(ARGS.config)
        return
    if not myconfig.CONFIG.basicAuthUser or not myconfig.CONFIG.basicAuthPass:
        print('set user/pasword in config.ini or use "-G" argument')
        return
    app.run(host='0.0.0.0', port=5006, debug=False)


if __name__ == '__main__':
    main()
