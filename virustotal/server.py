#!/usr/bin/env python

from contextlib import closing
from sqlite3 import connect
from bottle import request, template, route, run

@route('/virustotal/<db>')
def virus(db):
    with connect(db, timeout=10) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute('SELECT detected, count(*) FROM virus GROUP BY detected ORDER BY detected')
            return template('virustotal', title=db, cursor=cursor, refresh=request.query.refresh)

run(host='0.0.0.0')
