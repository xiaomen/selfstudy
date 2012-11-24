# -*- coding: utf-8 -*-

import datetime

days = [u'一', u'二', u'三', u'四', u'五', u'六', u'日']
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
    return 2 + (t.days - 1) / 7, date.weekday() + 1
