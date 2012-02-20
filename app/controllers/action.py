# -*- coding: utf-8 -*-
import web
from datetime import date

from config import jinja_env

from app.models import university
from app.models import building
from app.models import classroom
from app.models import filters
from app.helpers import utils

date_display_names = [u'今天', u'明天', u'后天']

class index:

    def GET(self, uni_param):
        if uni_param == 'favicon.ico':
            return ''
        today = date.today()
        allday = filters.get_allday_filter(uni_param)
        web.seeother('/{0}/buildings/{1}/{2}'.format(
                uni_param, today.isoformat(), allday['value']))

class classbuilding:

    def GET(self, uni_param, building_no, date_param, class_param):
        uni = university.get_university_by_no(uni_param)
        date = utils.str2date(date_param)
        class_list = map(lambda x:int(x), class_param.split('-'))

        bld = building.get_building_by_id(uni_param, building_no)
        bld['free_list'] = list(building.get_free_classes(uni_param, bld, date, class_list))
        allday = filters.get_allday_filter(uni_param)
        periods = filters.get_period_filter_list(uni_param)
        periods.insert(0, allday)

        return jinja_env.get_template('building.html').render(university=uni,
                query_date=date,
                query_class=class_param,
                dates=filters.get_select_date_list(3),
                date_names=date_display_names,
                periods=periods,
                classes=filters.get_class_filter_list(uni_param),
                building=bld)

class buildings:

    def GET(self, uni_param, date_param, class_param):
        uni = university.get_university_by_no(uni_param)
        date = utils.str2date(date_param)
        class_list = map(lambda x: int(x), class_param.split('-'))

        buildings = building.get_free_buildings(uni_param, date, class_list)
        allday = filters.get_allday_filter(uni_param)
        periods = filters.get_period_filter_list(uni_param)
        periods.insert(0, allday)

        return jinja_env.get_template('buildings.html').render(university=uni,
                query_date=date,
                query_class=class_param,
                dates=filters.get_select_date_list(3),
                date_names=date_display_names,
                periods=periods,
                classes=filters.get_class_filter_list(uni_param),
                buildings=buildings)

class room:

    def GET(self, uni_param, room_no):
        data = web.input()
        uni = university.get_university_by_no(uni_param)
        today = date.today()
        room = classroom.get_classroom_by_id(uni_param, room_no)
        bld = building.get_building_by_id(uni_param, room['class_building'])

        free_list = classroom.get_interval_free_time(uni_param, room, today, 7)
        room['free_list'] = free_list

        return jinja_env.get_template('classroom.html').render(university=uni,
                building=bld,
                query_date=data['date'],
                query_class=data['class'],
                classroom=room)
