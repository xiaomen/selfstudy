import web
from config import db

from app.models import calendar

from app.helpers import utils

def get_building_by_id(university, building_no):
    return web.listget(db.select('buildings',
        vars=dict(enabled=True, uni=university, no=building_no),
        where='enabled=$enabled and university=$uni and building_no=$no'), 0)
        
def get_buildings(university):
    return list(db.select('buildings',
        vars=dict(enabled=True, uni=university),
        where='enabled=$enabled and university=$uni'))

def get_free_classes(uni, building, date, class_list):
    week = calendar.get_calendar(uni, date).week_no
    day = date.isoweekday()
    occupies_int = utils.classlist2int(class_list)
    
    return db.select(['classrooms', 'occupations'],
            vars=dict(bld=building.building_no,
                week=week, day=day, ocp=occupies_int),
            where='''classroom=room_no and class_building=$bld and
                     week=$week and weekday=$day and occupies & $ocp=0''')

def get_free_buildings(uni, date, class_list):
    def f(x):
        x['free_count'] = len(get_free_classes(uni, x, date, class_list))
        return x

    buildings = get_buildings(uni)
    return map(f, buildings)
