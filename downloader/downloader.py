#!/usr/bin/env python

GOOGLE_LOGIN = GOOGLE_PASSWORD = AUTH_TOKEN = None

from humanfriendly import parse_size
from googleplay import GooglePlayAPI
from contextlib import closing
from argparse import ArgumentParser
from colorama import init, Fore
from config import *
import sqlite3
import os

init(autoreset=True)

create = 'CREATE TABLE IF NOT EXISTS download(pkg TEXT PRIMARY KEY, path TEXT)'
select = 'SELECT pkg,size FROM app WHERE pkg NOT IN (SELECT pkg FROM download)'
insert = 'INSERT INTO download VALUES(?,?)'

def sizeallowed(size, maxsize):
    try: return not maxsize or parse_size(size) <= maxsize
    except: return True

def mkdir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

class Downloader():

    def __init__(self):
        self.api = GooglePlayAPI(ANDROID_ID)
        self.api.login(GOOGLE_LOGIN, GOOGLE_PASSWORD, AUTH_TOKEN)

    def download(self, pkg, filename):
        doc = self.api.details(pkg).docV2
        vc = doc.details.appDetails.versionCode

        data = self.api.download(pkg, vc)
        with open(filename, 'wb') as apk:
            apk.write(data)

    def downloadall(self, dbname, outdir, maxsize=None):
        mkdir(outdir)
        with sqlite3.connect(dbname, timeout=10) as db:
            with closing(db.cursor()) as cur:
                cur.execute(create)
                for pkg, size in cur.execute(select).fetchall():
                    print 'Processing %s (%s) ...' % (pkg, size)
                    if not sizeallowed(size, maxsize):
                        print Fore.YELLOW + '  [SKIP: too big (%s)]' % size
                        continue
                    path = os.path.join(outdir, pkg + '.apk')
                    try:
                        self.download(pkg, path)
                    except Exception as e:
                        print Fore.RED + '  [ERROR: %s]' % e.message
                    else:
                        print Fore.GREEN + '  [OK: downloaded to %s]' % path
                        cur.execute(insert, (pkg, path))
                        db.commit()

if __name__ == '__main__':
    parser = ArgumentParser(description='get apks from Play Store')
    parser.add_argument('DB', help='sqlite3 apps db')
    parser.add_argument('-o', '--outdir', default='apks', help='output dir')
    parser.add_argument('-m', '--maxsize', default=0, help='max apk size')
    args = parser.parse_args()
    Downloader().downloadall(args.DB, args.outdir, parse_size(args.maxsize))

