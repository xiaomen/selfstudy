# -*- coding: utf-8 -*-

import string
import datetime
import random
import re
import web
import os

from sheep.api.statics import static_files
from jinja2 import Environment, FileSystemLoader

import model

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

class BuildingList:

    def GET(self, university, date_str='', class_str=''):
        if not model.is_university_exist(university):
            return 'error' #TODO
        now = model.generate_datetime()#TODO For test only
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
                date_str=date_str,
                class_str=class_str)

class Building:

    def GET(self, university, building_no, date_str='', class_str=''):
        self.db = web.database(dbn='mysql')
        
        if not model.is_university_exist(university):
            return 'error' #TODO
        if not model.is_building_exist(university, building_no):
            return 'error' #TODO
        now = model.generate_datetime()
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
                class_str=class_str)
        
class Classroom:

    def GET(self, university, classroom_no):
        if not model.is_university_exist(university):
            return 'error' #TODO
        if not model.is_classroom_exist(university, classroom_no):
            return 'error' #TODO
        classroom = model.get_classroom_info(classroom_no)
        now = model.generate_datetime()#TODO For test only
        free_list = model.get_classroom_free_time(university, classroom_no, now)
                    
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
