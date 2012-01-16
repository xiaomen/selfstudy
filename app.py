#!/usr/bin/python
# encoding: UTF-8
# a dummy wsgi app
from MySQLdb import *

def app(environ, start_response):
    db = connect()
    c = db.cursor()
    c.execute("select * from University")
    hnu_tuple = c.fetchone()
    print hnu_tuple
    name = hnu_tuple[1]
    short_name = hnu_tuple[2]
    print name + ' ' + short_name
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ["hello, world!!!" + short_name]
