# -*- coding: utf-8 -*-
import web

from datetime import date
from datetime import timedelta

from config import db

def get_select_date_list(length):
    return [date.today() + timedelta(days=i) for i in range(length)]

def get_period_list(university):
    return list(db.select('periods', vars=dict(uni=university),
        where='university=$uni'))

def get_class_assembling_list(university):
    return list(db.select('class_assembling', vars=dict(uni=university),
        where='university=$uni', order='start_no ASC'))

def get_allday_filter(university):
    allday = web.listget(db.select('classtimes',vars=dict(uni=university),
        what='max(class_no) as maxno',
        where='university=$uni'), 0)
    class_list = [str(i) for i in range(1, allday.maxno + 1)]
    return dict(display=u'全天', value='-'.join(class_list))

def get_period_filter_list(university):
    def period2obj(x):
        class_list = list(db.select('classtimes',
            vars=dict(uni=university, period=x.id),
            where='university=$uni and period=$period',
            order='class_no ASC'))
        class_list = map(lambda x: str(x.class_no), class_list)
        return dict(display=x.display, value='-'.join(class_list))
    
    return map(period2obj, get_period_list(university))

def get_class_filter_list(university):
    def assemble2obj(x):
        class_list = map(lambda x: str(x), range(x.start_no, x.end_no + 1))
        return dict(display=x.display, value='-'.join(class_list))

    return map(assemble2obj, get_class_assembling_list(university))
