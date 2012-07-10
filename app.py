#!/usr/local/bin/python2.7
#coding:utf-8

def app(e, s):
    1/0
    s('200 OK', [('Content-Type', 'text/html')])
    yield 'hw'
