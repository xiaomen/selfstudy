import json

from models import *

from sheep.api.cache import cache
from sheep.api.open import rpc

from sqlalchemy import and_
from sqlalchemy.sql.expression import desc

CACHE_EXPIRE_TIME = 86400 * 30

@cache('selfstudy:university:{uni_no}', CACHE_EXPIRE_TIME)
def get_university_by_no(uni_no):
    university = University.query.filter_by(no=uni_no).first()
    if not university:
        return None
    university.campus_list = university.campuses.all()
    for campus in university.campus_list:
        campus.building_list = campus.buildings.all()
    return university

@cache('selfstudy:buildings', CACHE_EXPIRE_TIME)
def get_buildings():
    buildings = Building.query.all()
    for building in buildings:
        building.classroom_list = Classroom.query \
                .filter_by(building_id=building.id) \
                .order_by(Classroom.name).all()
        building.campus = building.campus
    return buildings

@cache('selfstudy:building:{bid}', CACHE_EXPIRE_TIME)
def get_building_by_id(bid):
    building = Building.query.get(bid)
    if not building:
        return None
    building.classroom_list = Classroom.query \
                .filter_by(building_id=bid) \
                .order_by(Classroom.name).all()
    building.campus = building.campus
    return building

@cache('selfstudy:classroom:{cid}', CACHE_EXPIRE_TIME)
def get_classroom_by_id(cid):
    classroom = Classroom.query.get(cid)
    if not classroom:
        return None
    classroom.building = classroom.building
    classroom.building.campus = classroom.building.campus

    return classroom

def get_free_count(building, week, day, classes):
    return len(get_free_classrooms(building.id, building, week, day, classes))

@cache('selfstudy:free:{bid}:{week}:{day}:{classes}', CACHE_EXPIRE_TIME)
def get_free_classrooms(bid, building, week, day, classes):
    classes = [int(x) for x in classes.split('-')]
    alls = building.classroom_list
    occupies = set()
    for classroom, course in db.session.query(Classroom, Course). \
            filter(Classroom.building_id==bid). \
            filter(Classroom.id==Course.classroom_id). \
            filter(and_(Course.start_week <= week, week <= Course.end_week)). \
            filter(Course.day==day). \
            filter(Course.time.in_(classes)).all():
        if course.week_sign == 0 \
            or course.week_sign == 1 and week % 2 == 1 \
            or course.week_sign == 2 and week % 2 == 0:
                occupies.add(classroom.id)
                continue
    ret = []
    for a in alls:
        if a.id in occupies:
            continue
        ret.append(a)
    db.session.close()
    return ret

@cache('selfstudy:{classroom_id}:occupy:{week}:{day}', CACHE_EXPIRE_TIME)
def get_occupy_time(classroom_id, week, day):
    courses = Course.query.filter_by(classroom_id=classroom_id, day=day). \
            filter(and_(Course.start_week <= week, week <= Course.end_week)). \
            all()
    occupies = []
    for course in courses:
        if course.week_sign == 0 \
            or course.week_sign == 1 and week % 2 == 1 \
            or course.week_sign == 2 and week % 2 == 0:
                occupies.append(course.time)
    return occupies

#@cache('selfstudy:{building_id}:checkins', CACHE_EXPIRE_TIME)
def get_checkins_in_building(building_id):
    return CheckIn.query.filter_by(building_id=building_id) \
            .order_by(desc(CheckIn.timestamp)).all()

class Obj(object):
    pass

def get_user(uid):
    r = rpc('account', 'api/people/{0}'.format(uid))
    if r.get('status', None) == 'ok':
        user = Obj()
        user.uid = r.get('uid', None)
        user.name = r.get('name', None)
        user.domain = r.get('domain', None)
    else:
        user = None
    return user
