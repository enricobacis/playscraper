#!/usr/bin/env python

VIRUSTOTAL_APIKEY = None

from contextlib import closing, contextmanager
from argparse import ArgumentParser
from colorama import init, Fore
from config import *
from time import time
from glob import glob
from vt import VirusTotal
import humanfriendly as hf
import os.path
import sqlite3
import signal

init(autoreset=True)

create1 = 'CREATE TABLE IF NOT EXISTS virus (pkg PRIMARY KEY, id, uploaded, detected)'
create2 = 'CREATE TABLE IF NOT EXISTS download (pkg PRIMARY KEY, path TEXT)'
select1 = 'SELECT pkg, path FROM download WHERE pkg NOT IN (SELECT pkg FROM virus) LIMIT 1'
select2 = 'SELECT pkg, id FROM virus WHERE detected BETWEEN -2 AND -1 AND uploaded < ? LIMIT 2'
insert = 'INSERT INTO virus VALUES (?, ?, ?, ?)'
update = 'UPDATE virus SET detected = ? WHERE pkg = ?'
reschedule = 'UPDATE virus SET uploaded = ?, detected = (detected - 1) WHERE pkg = ?'

def exit():
    raise SystemExit

class Checker():

    def __init__(self, dbname, basedir):
        self.api = VirusTotal(VIRUSTOTAL_APIKEY)
        self.basedir = basedir
        self.dbname = dbname
        with self.getdbcursor() as (db, cursor):
            cursor.execute(create1)
            cursor.execute(create2)

    @contextmanager
    def getdbcursor(self):
        with sqlite3.connect(self.dbname, timeout=10) as db:
            db.text_factory = str
            with closing(db.cursor()) as cursor:
                yield db, cursor
            db.commit()

    def scan(self):
        with self.getdbcursor() as (db, cursor):
            selected = cursor.execute(select1).fetchall()
            for pkg, path in selected:
                print Fore.BLUE + 'Uploading %s for scan ...' % pkg,
                path = os.path.abspath(os.path.join(self.basedir, path))
                if os.path.getsize(path) >= hf.parse_size('32M'):
                    cursor.execute(insert, (pkg, "file-too-big", "", -100))
                    print Fore.RED + 'File too big for VirusTotal'
                    continue
                try:
                    id = self.api.scan(path)
                    cursor.execute(insert, (pkg, id, time(), -1))
                    print Fore.GREEN + 'OK'
                except:
                    cursor.execute(insert, (pkg, "api-scan-error", "", -100))
                    print Fore.RED + 'API Error'
                db.commit()
        return len(selected)

    def result(self):
        with self.getdbcursor() as (db, cursor):
            selected = cursor.execute(select2, [time() - 7200]).fetchall()
            for pkg, id in selected:
                try:
                    detected = self.api.get_percent_detected(id)
                    cursor.execute(update, (detected, pkg))
                    print '{} [{} --> {:.0%} virus]'.format(Fore.GREEN
                        if not detected else Fore.YELLOW, pkg, detected)
                except:
                    cursor.execute(reschedule, (time(), pkg))
                    print Fore.MAGENTA + ' [%s API Error -> rescheduling]' % pkg
                db.commit()

        return len(selected)

    def checkall(self):
        while any((self.scan(), self.result())): pass
        print 'Everything done for now'
        exit()

    def addtodownload(self):
        with self.getdbcursor() as (db, cursor):
            for apk in glob(os.path.join(self.basedir, '*.apk')):
                apk = os.path.basename(apk)
                pkg = os.path.splitext(apk)[0]
                cursor.execute('INSERT OR IGNORE INTO download VALUES (?, ?)', (pkg, apk))
            db.commit()
        print Fore.CYAN + '[all apks added to download table]'

if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit)
    parser = ArgumentParser(description='Check apks with VirusTotal')
    parser.add_argument('DB', help='sqlite3 apps db')
    parser.add_argument('-b', '--basedir', default='.', help='base apk dir')
    parser.add_argument('-a', '--add', action='store_true', help='add apks')
    args = parser.parse_args()
    checker = Checker(args.DB, args.basedir)
    if args.add: checker.addtodownload()
    checker.checkall()

