from models import *
from sheep.api.cache import cache
from sqlalchemy import and_

@cache('selfstudy:university:{uni_no}', 86400)
def get_university_by_no(uni_no):
    university = University.query.filter_by(no=uni_no).first()
    university.campus_list = university.campuses.all()
    for campus in university.campus_list:
        campus.building_list = campus.buildings.all()
    return university

@cache('selfstudy:buildings', 86400)
def get_buildings():
    buildings = Building.query.all()
    for building in buildings:
        building.classroom_list = building.classrooms.all()
        building.campus = building.campus
    return buildings

@cache('selfstudy:building:{bid}', 86400)
def get_building_by_id(bid):
    building = Building.query.get(bid)
    building.classroom_list = building.classrooms.all()
    building.campus = building.campus
    return building

@cache('selfstudy:classroom:{cid}', 86400)
def get_classroom_by_id(cid):
    classroom = Classroom.query.get(cid)

    classroom.building = classroom.building
    classroom.building.campus = classroom.building.campus

    return classroom

def get_free_count(building, week, day, classes):
    return len(get_free_classrooms(building, week, day, classes))

def get_free_classrooms(building, week, day, classes):
    return filter(lambda c: is_free(c.id, week, day, classes), building.classroom_list)
    
@cache('selfstudy:{classroom_id}:is_free:{week}:{day}:{classes}', 86400)
def is_free(classroom_id, week, day, classes):
    courses = Course.query.filter_by(classroom_id=classroom_id, day=day). \
            filter(and_(Course.start_week <= week, week <= Course.end_week)). \
            filter(Course.time.in_(classes)).all()
    for course in courses:
        if course.week_sign == 0 \
            or course.week_sign == 1 and week % 2 == 1 \
            or course.week_sign == 2 and week % 2 == 0:
                return False
    return True 

@cache('selfstudy:{classroom_id}:occupy:{week}:{day}', 86400)
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
