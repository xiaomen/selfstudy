# -*- coding: utf-8 -*-

import string
import datetime
import random
import re
import web
import os
import json

from sheep.api.statics import static_files
from jinja2 import Environment, FileSystemLoader

import model

urls = (
    '/(.*)/buildings/(.*)/(.*)', 'BuildingList',
    '/(.*)/', 'Redirect',
    )

jinja_env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),
                            'templates')),
    extensions=['jinja2.ext.loopcontrols'])
jinja_env.globals.update({})
jinja_env.filters['s_files'] = static_files

class BuildingList:

    def GET(self, university, date_str='', class_str=''):
        if not model.is_university_exist(university):
            return 'error' #TODO
        now = model.generate_datetime(date_str)#TODO For test only
        if now == None:
            return 'error' #TODO
        if class_str == '':
            class_no = model.get_class_no(university, now)
            if class_no == None:
                return 'It\'s too late, all classrooms are closed'#TODO
        else:
            if not model.is_class_no_exist(university, class_str):
                return 'error' #TODO
            class_no = class_str
        buildings = model.get_buildings(university, now, class_no)
        return jinja_env.get_template('index.html').render(
                buildings=buildings,
                university=university,
                weekday=now.isoweekday(),
                date_str=date_str,
                class_str=class_str)

class BuildingData:
    def GET(self, university, building_no, date_str=''):
        if not model.is_university_exist(university):
            return 'error'
        if not model.is_building_exist(university, building_no):
            return 'error'
        date = model.generate_datetime(date_str)
        building = model.get_building_data(university, building_no, date)
        return json.dumps(building)

class Building:

    def GET(self, university, building_no, date_str='', class_str=''):
        
        if not model.is_university_exist(university):
            return 'error' #TODO
        if not model.is_building_exist(university, building_no):
            return 'error' #TODO
        now = model.generate_datetime(date_str)
        if now == None:
            return 'error'#TODO
        if class_str == '':
            class_no = model.get_class_no(university, now)
            if class_no == None:
                return 'It\'s too late, all classrooms are closed'#TODO
        else:
            if not model.is_class_no_exist(university, class_str):
                return 'error' #TODO
            class_no = class_str
        building = model.get_building(university, building_no, now, class_no)
        return jinja_env.get_template('building_result.html').render(
                building=building,
                university=university,
                date_str=date_str,
                weekday=now.isoweekday(),
                class_str=class_str)
        
class Classroom:

    def GET(self, university, classroom_no):
        if not model.is_university_exist(university):
            return 'error' #TODO
        if not model.is_classroom_exist(university, classroom_no):
            return 'error' #TODO
        classroom = model.get_classroom_info(classroom_no)
        building = model.get_building_by_classroom(classroom_no)
        now = model.generate_datetime()
        free_list = model.get_classroom_free_time(university, classroom_no, now)
        return jinja_env.get_template('classroom_result.html').render(
                classroom=classroom,
                university=university,
                building=building,
                now_date=now,
                free_list=free_list)
class DateSelect:
    
    def GET(self, university):
        if not model.is_university_exist(university):
            return 'error' #TODO
        now = model.generate_datetime()
        date_list = [now + datetime.timedelta(days=i) for i in range(0, 7)]
        return jinja_env.get_template('date_select.html').render(
                date_list=date_list,
                university=university)

class TimeSelect:
    
    def GET(self, university, date_str):
        if not model.is_university_exist(university):
            return 'error' #TODO
        now = model.generate_datetime(date_str)
        if date_str == '' or now == None:
            return 'error' #TODO
        time_list = model.get_time_list(university)
        return jinja_env.get_template('time_select.html').render(
                time_list=time_list,
                select_date = now,
                university=university)

class Redirect:
    def GET(self, path):
        web.seeother('/' + path)

class Query:
    def GET(self, university, classroom):
        return 'Hello World'

app = web.application(urls, globals())
wsgi_app = app.wsgifunc()

if __name__ == "__main__":
    app.run()
