# curl -i -H "Content-Type: application/json" -X POST -d '{"torpath" : "~/torccf/frds_10018_tt6710716/真探S03.2019.1080p.WEB-DL.x265.AC3￡cXcY@FRDS", "torhash": "289256b0918c3dccea51a194a3e834664b17eafd", "torsize": "11534336"}' http://localhost:5000/api/torcp

from flask import Flask, render_template, jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sys
import os
from torcp.torcp import Torcp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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
            'torsite': self.torsite,
            'torsiteid': self.torsiteid,
            'torsitecat': self.torsitecat,
            'torimdb': self.torimdb,
            'tmdbid': self.tmdbid,
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
        query = db.session.query(TorMediaItem).filter(TorMediaItem.torhash == qbhash).first()
        return query


@app.route('/')
def index():
    return render_template('ajax_table.html', title='Ajax Table')


@app.route('/api/data')
def data():
    return {'data': [tor.to_dict() for tor in TorMediaItem.query]}


@app.route('/api/torcp', methods=['POST'])
def runTorcp():
    if 'torpath' in request.json and 'torhash' in request.json and 'torsize' in request.json:
        npath = os.path.normpath(request.json['torpath'].strip())
        torname = os.path.basename(npath)
        site_id_imdb = os.path.basename(os.path.dirname(npath))
        site = ''
        siteid = ''
        torimdb = ''
        if "_" in site_id_imdb:
            l = site_id_imdb.split("_")
            if len(l) == 3:
                site, siteid, torimdb = l[0], l[1], l[2]
            elif len(l) == 2:
                site, siteid = l[0], l[1]

        argv = [npath, "-d", "~/torccf/result", "-s", "--lang", "cn,ja,ko", "--tmdb-api-key",
                "9e0791be4a66b90b471e6d3c4674e084", "--make-log", "--emby-bracket", "--extract-bdmv", "--tmdb-origin-name"]
        eo = TorcpItemDBObj(site, siteid, torimdb, 
                            request.json['torhash'].strip(), 
                            request.json['torsize'].strip())
        o = Torcp()
        o.main(argv, eo)
        return jsonify({'OK': 200}), 200
    return jsonify({'Error': 401}), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
