import random
import string
import datetime
import re
import web

db = web.database(dbn='mysql')

def generate_datetime(date_str=''):
    ret_time = ''
    if date_str == '':
        year = 2012
        month = random.randint(2, 6)
        day = random.randint(1, 30)
        hour = random.randint(8, 21)
        minute = random.randint(0, 59)
        return datetime.datetime(year, month, day, hour, minute)
    else:
        try:
            ret_time = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except:
            ret_time = None
    return ret_time

def get_class_no(university, timestamp):
    time_list = db.select('Class_Time',
            dict(name=university, time=timestamp.time()),
            where='university=$name and start_time<$time and $time<end_time')
    if time_list == None or len(time_list) == 0:
        time_list = db.select('Class_Time',
                dict(name=university, time=timestamp.time()),
                where='university=$name and $time<start_time',
                order='class_no ASC')
        if time_list == None or len(time_list) == 0:
            return None
    time = time_list[0].class_no
    return '{0:02}'.format(time)
    
def is_class_no_exist(university, class_no):
    rows = db.select('Class_Time',
            dict(uni=university),
            what='class_no',
            where='university=$uni')
    class_time_list = '' 
    for row in rows:
        class_time_list += '{0:02}'.format(row.class_no)
    return class_time_list.find(class_no) % 2 == 0

def is_classroom_exist(university, classroom):
    pattern = re.compile('\w{,10}')
    if pattern.match(university) == None or pattern.match(classroom) == None:
        return False
    rows = db.select(
            ['Class_Building', 'Classroom'],
            dict(uni=university, classroom=classroom),
            where="""class_building=building_no and
                           university=$uni and
                           room_no=$classroom and enabled=1""")
    return rows != None and len(rows) > 0 

def get_calendar_info(university, timestamp):
    vars = dict(name=university, date=timestamp.date())
    calendar_list = db.select('School_Calendar',
            vars,
            where='university=$name and datediff($date,start_date)<7',
            order='week_no ASC')
    calendar = calendar_list[0]
    return calendar 

def is_university_exist(university):
    pattern = re.compile('\w{,10}')
    if pattern.match(university) == None:
        return False
    rows = db.select('University',
            dict(name=university),
            where='short_name=$name')
    return rows != None and len(rows) > 0 

def is_building_exist(university, building):
    pattern = re.compile('\w{,10}')
    if pattern.match(university) == None or pattern.match(building) == None:
        return False
    rows = db.select('Class_Building',
            dict(enabled=True, uni=university, bld=building),
            where='university=$uni and building_no=$bld and enabled=$enabled')
    return rows != None and len(rows) > 0 

def is_classroom_exist(university, classroom):
    pattern = re.compile('\w{,10}')
    if pattern.match(university) == None or pattern.match(classroom) == None:
        return False
    rows = db.select(['Class_Building', 'Classroom'],
            dict(enabled=True, uni=university, classroom=classroom),
            where="""class_building=building_no and
                           university=$uni and
                           room_no=$classroom and
                           enabled=$enabled""")
    return rows != None and len(rows) > 0 

def get_calendar_info(university, timestamp):
    calendar_list = db.select('School_Calendar',
            dict(name=university, date=timestamp.date()),
            where='university=$name and datediff($date,start_date)<7',
            order='week_no ASC')
    calendar = calendar_list[0]
    return calendar.week_no

def get_free_class_list(university, building_no, week, day, class_no):

    where_sql = """room_no=classroom and
                   class_building=$building and
                   start_week_no<=$week and $week<=end_week_no and
                   day_no=$day and 
                   (week_sign=1 or week_sign=
                   (case $week%2 when 0 then 3
                    else 2 end)) and
                   INSTR(class_time, $class_no)>0"""
    free_list = []
    occupy_list = []
    vars=dict(building=building_no,
            week=week,
            day=day,
            class_no=class_no)
    class_list = db.select('Classroom',vars,
            where='class_building=$building')
    rows = db.select(['Classroom', 'Class_Occupation'],
            vars, where=where_sql)
    occupy_list = list(rows)
    for c in class_list:
        find = False
        for occupy in occupy_list:
            if c.room_no == occupy.room_no:
                find = True
                break
        if not find:
            free_list.append(c)
    return free_list


def get_buildings(university, date, class_no):
    
    week = get_calendar_info(university, date)
    day = date.isoweekday()
    building_list = db.select('Class_Building',
            dict(enabled=True, university=university),
            what='name, building_no',
            where='enabled=$enabled and university=$university')
    ret_buildings = []
    for building in building_list:
        class_list = get_free_class_list(university,
                building.building_no,
                week,
                day,
                class_no)
        if len(class_list) > 3:
            building['free_list'] = class_list[0:3]
        else:
            building['free_list'] = class_list
        ret_buildings.append(building)
    return ret_buildings

def get_building(university, building_no, date, class_no):
    building = db.select('Class_Building',
            dict(uni=university, bld=building_no, enabled=True),
            where='university=$uni and building_no=$bld')[0]
    week = get_calendar_info(university, date)
    day = date.isoweekday()
    free_list = get_free_class_list(university,
            building.building_no,
            week,
            day,
            class_no)
    building['free_list'] = free_list
    return building

def get_classroom_info(classroom_no):
    classroom = db.select('Classroom',
            dict(classroom=classroom_no),
            where='room_no=$classroom')
    return classroom[0]

def split_str(s):
    ret = []
    if s != None:
        while len(s) > 0:
            ret.append(s[0:2])
            s = s[2:]
    return ret
def get_class_free_time_of_day(classroom_no, week, day, class_time_list):
    where_sql = """classroom=$classroom and
                   start_week_no<=$week and $week<=end_week_no and
                   day_no=$day and 
                   (week_sign=$sign or
                   week_sign=
                   (case $week%2 when 0 then 3
                    else 2 end))""" 
    vars = dict(classroom=classroom_no,
            week=week,
            day=day,
            sign=1)
    rows = db.select('Class_Occupation', vars, where=where_sql)
    occupy_list = [x.class_time for x in list(rows)]
    free_list = []
    for time in class_time_list:
        find = False
        f_time = '{0:02}'.format(time)
        for occupy_time in occupy_list:
            o_list = split_str(occupy_time)
            if f_time in o_list:
                find = True
                break
        if not find:
            free_list.append(time)
    return free_list
 
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

def get_classroom_free_time(university, classroom_no, date):
    rows = db.select('Class_Time',
            dict(uni=university),
            where='university=$uni')
    class_time_list = [x.class_no for x in list(rows)]
    rows = db.select('Class_Time_Assembling',
            dict(uni=university),
            where='university=$uni')
    class_time_assembling = list(rows)
    free_list = []
    for i in range(0, 7):
        time = date + datetime.timedelta(days=i)
        time_list = get_class_free_time_of_day(classroom_no,
                get_calendar_info(university, time),
                time.isoweekday(),
                class_time_list)
        time_list = merge_time(time_list, class_time_assembling)
        free_list.append(dict(time=time, time_list=time_list))
    return free_list

def get_time_value(start, end):
    ret = ''
    for i in range(start, end + 1):
        ret += '{0:02}'.format(i)
    return ret

def get_class_quantity(university):
    rows = db.select('Class_Time', dict(uni=university),
            what='max(class_no)', where='university=$uni')
    return rows[0]

def get_time_list(university):
    rows = db.select('Class_Time_Assembling',
            dict(uni=university),
            where='university=$uni',
            order='start_no ASC')
    return [dict(value=get_time_value(x.start_no, x.end_no), display=x.display)
            for x in rows]

def get_building_by_classroom(classroom_no):
    rows = db.select(['Class_Building', 'Classroom'],
            dict(classroom=classroom_no),
            what="Class_Building.name as name",
            where="""class_building=building_no and
                     room_no=$classroom""")
    return rows[0]

def occupy_str_to_set(class_str):
    if class_str == None:
        return None
    ret = set()
    while len(class_str) > 0:
        ret.add(string.atoi(class_str[0:2]))
        class_str = class_str[2:]
    return ret

def get_building_data(university, building_no, date):
    where_sql = """room_no=classroom and
                   class_building=$building and
                   start_week_no<=$week and $week<=end_week_no and
                   day_no=$day and 
                   (week_sign=1 or week_sign=
                   (case $week%2 when 0 then 3
                    else 2 end))"""
    building = db.select('Class_Building',
            dict(uni=university, bld=building_no, enabled=True),
            where='university=$uni and building_no=$bld')[0]
    building['class_quantity'] = get_class_quantity(university)['max(class_no)']
    week = get_calendar_info(university, date)
    day = date.isoweekday()

    vars=dict(building=building_no,
            week=week,
            day=day)

    rows = db.select('Classroom',vars,
            where='class_building=$building')
    class_list = list(rows)

    rows = db.select(['Classroom', 'Class_Occupation'],
            vars, where=where_sql)
    occupy_list = list(rows)
    for c in class_list:
        s = set()
        for occupy in occupy_list:
            if c.room_no != occupy.room_no:
                continue
            s |= occupy_str_to_set(occupy.class_time)
        c['occupy_list'] = list(s)
    building['class_list'] = class_list
    return building        
   

