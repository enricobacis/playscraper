#!/usr/bin/env python

VIRUSTOTAL_APIKEY = None

from contextlib import closing
from argparse import ArgumentParser
from colorama import init, Fore
from os.path import join
from config import *
from time import time
from vt import VirusTotal
import sqlite3
import signal

init(autoreset=True)

create = ('CREATE TABLE IF NOT EXISTS virus (pkg PRIMARY KEY, id, uploaded, detected)')
select1 = 'SELECT pkg, path FROM download WHERE pkg NOT IN (SELECT pkg FROM virus) LIMIT 1'
select2 = 'SELECT pkg, id FROM virus WHERE detected = -1 AND uploaded < ? LIMIT 1'
insert = 'INSERT INTO virus VALUES (?, ?, ?, -1)'
update = 'UPDATE virus SET detected = ? WHERE pkg = ?'

def exit():
    raise SystemExit

class Checker():

    def __init__(self, basepath):
        self.api = VirusTotal(VIRUSTOTAL_APIKEY)
        self.basepath = basepath

    def scan(self, db):
        with closing(db.cursor()) as cursor:
            selected = cursor.execute(select1).fetchall()
            for pkg, path in selected:
                print Fore.BLUE + 'Uploading %s for scan ...' % pkg
                id = self.api.scan(join(self.basepath, path))
                cursor.execute(insert, (pkg, id, time()))
                db.commit()
        return len(selected)

    def result(self, db):
        with closing(db.cursor()) as cursor:
            selected = cursor.execute(select2, [time() - 3600]).fetchall()
            for pkg, id in selected:
                detected = self.api.get_percent_detected(id)
                cursor.execute(update, (detected, pkg))
                print '{} [{} --> {:.0%} virus]'.format(Fore.GREEN
                    if not detected else Fore.YELLOW, pkg, detected)
        return len(selected)

    def createtable(self, db):
        with closing(db.cursor()) as cursor:
            cursor.execute(create)
            db.commit()

    def checkall(self, dbname):
        with sqlite3.connect(dbname, timeout=10) as db:
            self.createtable(db)
            while True:
                scanned = self.scan(db)
                resulted = self.result(db)
                if not scanned and not resulted:
                    print 'Everything done for now'
                    break
        exit()

if __name__ == '__main__':
    parser = ArgumentParser(description='Check apks with VirusTotal')
    parser.add_argument('DB', help='sqlite3 apps db')
    parser.add_argument('-b', '--basedir', default='.', help='base apk dir')
    args = parser.parse_args()
    signal.signal(signal.SIGINT, exit)
    Checker(args.basedir).checkall(args.DB)

