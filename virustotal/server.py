#!/usr/bin/env python

from contextlib import closing
from sqlite3 import connect
from os.path import isfile
from bottle import request, template, route, run

@route('/virustotal/<db>')
def virus(db):
    if not isfile(db):
        return 'The database does not exist: "%s"' % db
    with connect(db, timeout=10) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute("SELECT CAST(0.999 + detected * 10 AS INT) || '0% virus' AS score, count(*)"
                           " FROM virus WHERE detected >= 0 GROUP BY score ORDER BY score")
            return template('virustotal', title=db, cursor=cursor, refresh=request.query.refresh)

run(host='0.0.0.0')

