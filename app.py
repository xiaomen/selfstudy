# -*- coding: utf-8 -*-

import string
import datetime
import random
import re
import web
import os

from sheep.api.statics import static_files
from jinja2 import Environment, FileSystemLoader
from MySQLdb import *

urls = (
    '/(.*)/buildings', 'BuildingList',
    '/(.*)/buildings/(.*)/(.*)', 'BuildingList',
    '/(.*)/building/(.*)/(.*)/(.*)', 'Building', 
    '/(.*)/building/(.*)', 'Building', 
    '/(.*)/classroom/(.*)', 'Classroom',
    '/(.*)/(.*)', 'Query'
    )

jinja_env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),
                            'templates')),
    extensions=['jinja2.ext.loopcontrols'])
jinja_env.globals.update({})
jinja_env.filters['s_files'] = static_files

def generate_datetime():
    """
    This Function will return a random datetime in a semester.
    Only for test.
    """
    year = 2011
    month = random.randint(9, 12)
    day = random.randint(1,30)
    hour = random.randint(8, 21)
    minute = random.randint(0, 59)
    return datetime.datetime(year, month, day, hour, minute)

def is_university_exist(db, university):
    pattern = re.compile('\w{,10}')
    if pattern.match(university) == None:
        return False
    vars = dict(name=university)
    rows = db.select('University',
            vars, where='short_name=$name')
    return rows != None and len(rows) > 0 

def is_building_exist(db, university, building):
    pattern = re.compile('\w{,10}')
    if pattern.match(university) == None or pattern.match(building) == None:
        return False
    vars = dict(uni=university, bld=building)
    rows = db.select('Class_Building',
            vars, where='university=$uni and building_no=$bld and enabled=1')
    return rows != None and len(rows) > 0 

def is_classroom_exist(db, university, classroom):
    pattern = re.compile('\w{,10}')
    if pattern.match(university) == None or pattern.match(classroom) == None:
        return False
    vars = dict(uni=university, classroom=classroom)
    rows = db.select(['Class_Building', 'Classroom'],
            vars, where="""class_building=building_no and
                           university=$uni and
                           room_no=$classroom and enabled=1""")
    return rows != None and len(rows) > 0 


def get_calendar_info(db, university, timestamp):
    vars = dict(name=university, date=timestamp.date())
    calendar_list = db.select('School_Calendar',
            vars,
            where='university=$name and datediff($date,start_date)<7',
            order='week_no ASC')
    calendar = calendar_list[0]
    return calendar 

def class_display2value(display):
    start_no = display.split('-')[0]
    end_no = display.split('-')[1]
    ret_str = ''
    for i in range(string.atoi(start_no), string.atoi(end_no) + 1):
        ret_str += '{0:02}'.format(i)
    return ret_str

def get_class_no(db, university, timestamp):
    vars = dict(name=university, time=timestamp.time())
    time_list = db.select('Class_Time',
            vars,
            where='university=$name and start_time<$time and $time<end_time')
    if time_list == None or len(time_list) == 0:
        time_list = db.select('Class_Time',
                vars,
                where='university=$name and $time<start_time',
                order='class_no ASC')
        if time_list == None or len(time_list) == 0:
            return None
    time = time_list[0].display
    ret_str = class_display2value(time)
    if ret_str == '091011':
        ret_str = '0910'
    print ret_str
    return ret_str

def get_free_class_list(db, university, building_no, week, day, class_no):

    where_sql = """room_no=classroom and
                   class_building=$building and
                   start_week_no<=$week and $week<=end_week_no and
                   day_no=$day and week_sign=$sign and
                   INSTR(class_time, $class_no)>0"""
    free_list = []
    occupy_list = []
    vars=dict(building=building_no, week=week, day=day, class_no=class_no, sign=1)
    class_list = db.select('Classroom',vars,
            where='class_building=$building')
    results = db.select(['Classroom', 'Class_Occupation'],
            vars, where=where_sql)
    for r in results:
        occupy_list.append(r)
    if week % 2 == 0:
        vars['sign'] = 3
    else:
        vars['sign'] = 2
    results = db.select(['Classroom', 'Class_Occupation'],
            vars, where=where_sql)
    for r in results:
        occupy_list.append(r)

    for c in class_list:
        find = False
        for occupy in occupy_list:
            if c.room_no == occupy.room_no:
                find = True
                break
        if not find:
            free_list.append(c)
    return free_list

class BuildingList:

    def GET(self, university, date_str='', class_str=''):
        self.db = web.database(dbn='mysql')
        if not is_university_exist(self.db, university):
            return 'error' #TODO
        class_no = ''
        if date_str == '' and class_str == '':
            now = generate_datetime()#TODO For test only
            class_no = get_class_no(self.db, university, now)
        elif len(date_str) * len(class_str) == 0:
            return 'error' #TODO
        else:
            try:
                now = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                rows = self.db.select('Class_Time',
                        dict(uni=university),
                        where='university=$uni')
                class_time_list = []
                for row in rows:
                    class_time_list.append(class_display2value(row.display))
                if not class_str in class_time_list:
                    return 'error'#TODO
                if class_str == '091011':
                    class_str = '0910'
                class_no = class_str
            except:
               return 'date format error'#TODO

        print 'now is {0}, class_no is {1}'.format(now, class_no)
        week = get_calendar_info(self.db, university, now).week_no
        day = now.isoweekday()
        if class_no == None:
            return 'It\'s too late, all classrooms are closed'
        class_dict = {}
        building_list = self.db.select('Class_Building',
                dict(enabled=True, university=university),
                where='enabled=$enabled and university=$university')
        ret_building_list = []
        for building in building_list:
            ret_building_list.append(building)
            free_list = get_free_class_list(self.db, university, building.building_no, week, day, class_no)
            class_dict[building.building_no] = free_list 
        return jinja_env.get_template('index.html').render(
                buildings=ret_building_list,
                class_dict=class_dict,
                university=university,
                date_str=date_str,
                class_str=class_str)

class Building:

    def GET(self, university, building_no, date_str='', class_str=''):
        self.db = web.database(dbn='mysql')
        
        if not is_university_exist(self.db, university):
            return 'error' #TODO
        if not is_building_exist(self.db, university, building_no):
            return 'error' #TODO
        class_no = ''
        if date_str == '' and class_str == '':
            now = generate_datetime()#TODO For test only
            class_no = get_class_no(self.db, university, now)
        elif len(date_str) * len(class_str) == 0:
            return 'error' #TODO
        else:
            try:
                now = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                rows = self.db.select('Class_Time',
                        dict(uni=university),
                        where='university=$uni')
                class_time_list = []
                for row in rows:
                    class_time_list.append(class_display2value(row.display))
                if not class_str in class_time_list:
                    return 'error'#TODO
                if class_str == '091011':
                    class_str = '0910'
                class_no = class_str
            except:
               return 'date format error'#TODO

        building = self.db.select('Class_Building',
                dict(uni=university, bld=building_no, enabled=True),
                where='university=$uni and building_no=$bld and enabled=$enabled')[0]
        week = get_calendar_info(self.db, university,now).week_no
        day = now.isoweekday()
        if class_no == None:
            return 'It\'s too late, all classrooms are closed'

        free_list = get_free_class_list(self.db, university, building.building_no, week, day, class_no)

        return jinja_env.get_template('building_result.html').render(
                building=building,
                university=university,
                date_str=date_str,
                class_str=class_str,
                class_list=free_list)
        
def get_free_time(db, classroom_no, week, day, class_time_list):
    where_sql = """classroom=$classroom and
                   start_week_no<=$week and $week<=end_week_no and
                   day_no=$day and week_sign=$sign and
                   INSTR(class_time, $class_no)>0"""
    ret_list = []
    for class_time in class_time_list:
        class_no = class_display2value(class_time)[0:4]
        vars = dict(classroom=classroom_no, week=week, day=day, sign=1, class_no=class_no)
        results = db.select('Class_Occupation', vars, where=where_sql)
        if results == None or len(results) == 0:
            ret_list.append(class_time)
    return ret_list
    
class Classroom:

    def GET(self, university, classroom_no):
        self.db = web.database(dbn='mysql')
        if not is_university_exist(self.db, university):
            return 'error' #TODO
        if not is_classroom_exist(self.db, university, classroom_no):
            return 'error' #TODO
        rows = self.db.select('Class_Time',
                dict(uni=university),
                where='university=$uni')
        class_time_list = []
        for row in rows:
            class_time_list.append(row.display)

        classroom = self.db.select('Classroom', dict(classroom=classroom_no),
                where='room_no=$classroom')
        now = generate_datetime()#TODO For test only
        free_list = []
        for i in range(0, 7):
            time = now + datetime.timedelta(days=i)
            week = get_calendar_info(self.db, university, time).week_no
            day = time.isoweekday()
            time_list = get_free_time(self.db, classroom_no, week, day, class_time_list)
            free_list.append(dict(weekday=day, time_list=time_list))
                    
        return jinja_env.get_template('classroom_result.html').render(
                classroom=classroom,
                university=university,
                free_list=free_list)
        
class Query:
    def GET(self, university, classroom):
        db = web.database(dbn='mysql')
        entries = db.select('Class_Building')
        return [x for x in entries]
        #return 'Hello World!{0} {1}'.format(university, classroom)

app = web.application(urls, globals())
wsgi_app = app.wsgifunc()

if __name__ == "__main__":
    app.run()
