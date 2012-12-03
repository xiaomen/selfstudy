# -*- coding: utf-8 -*-

import datetime
from functools import wraps

days = [u'一', u'二', u'三', u'四', u'五', u'六', u'日']

def unicoded(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        reval = method(*args, **kwargs)
        if isinstance(reval, str):
            return reval.decode('utf-8')
        return reval
    return wrapper

def str2date(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

def classlist2int(class_list):
    def add(x, y): return x + (1 << (y - 1))
    return reduce(add, class_list, 0)

def int2bitarray(n, length):
    return map(lambda x: n & (1 << x) != 0, range(length))

def int2classes(occupies, length):
    return filter(lambda x: occupies & (1 << (x - 1)) == 0,
            range(1, length + 1))

def get_select_date_list(length):
    today = datetime.date.today()
    return map(lambda x: today + datetime.timedelta(days=x), range(length))

def merge_time(time_list, assembling):
    ret_list = []
    time_set = set(time_list)
    for i in assembling:
        s = set(range(i.start_no, i.end_no + 1))
        if s <= time_set:
            ret_list.append(i.display)
        elif not time_set.isdisjoint(s):
            ret_list.extend(list(time_set & s))
    return ret_list

def get_date_filters():
    i = datetime.date.today().isoweekday() - 1
    names = [u'今天(周{0})'.format(days[i]), u'明天', u'后天']
    return zip(get_select_date_list(3), names)

def get_interval_date(length):
    dates = get_select_date_list(length)
    names = map(lambda x: u'周{0}'.format(days[x.isoweekday() - 1]), dates)
    names[0] = u'今天'
    return zip(dates, names)

def get_week_and_day(date, university):
    t = date - university.start_date
    if t == 0:
        return 1, 7
    return 1 + t.days / 7, date.weekday() + 1

@unicoded
def timeago(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime as dt
    now = dt.now()
    if type(time) is int:
        diff = now - dt.fromtimestamp(time)
    elif isinstance(time, dt):
        diff = now - time 
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "刚才"
        if second_diff < 60:
            return str(second_diff) + " 秒前"
        if second_diff < 120:
            return  "1 分钟前"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " 分钟前"
        if second_diff < 7200:
            return "1 小时前"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " 小时前"
    if day_diff == 1:
        return "昨天"
    if day_diff == 2:
        return "前天"
    if day_diff < 7:
        return str(day_diff) + " 天前"
    if day_diff < 31:
        return str(day_diff/7) + " 周前"
    if day_diff < 365:
        return str(day_diff/30) + " 月前"
    return str(day_diff/365) + " 年前"
