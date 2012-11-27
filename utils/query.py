from models import *
from sqlalchemy import and_

def get_university_by_no(no):
    return University.query.filter_by(no=no).first()

def get_building_by_id(bid):
    return Building.query.get(bid)

def get_classroom_by_id(cid):
    return Classroom.query.get(cid)

def get_free_count(building, week, day, classes):
    return len(get_free_classrooms(building, week, day, classes))

def get_free_classrooms(building, week, day, classes):
    return filter(lambda c: is_free(c, week, day, classes), building.classrooms.all())
    
def is_free(classroom, week, day, classes):
    courses = Course.query.filter_by(classroom_id=classroom.id, day=day). \
            filter(and_(Course.start_week <= week, week <= Course.end_week)). \
            filter(Course.time.in_(classes)).all()
    for course in courses:
        if course.week_sign == 0 \
            or course.week_sign == 1 and week % 2 == 1 \
            or course.week_sign == 2 and week % 2 == 0:
                return False
    return True 

def get_occupy_time(classroom, week, day):
    courses = Course.query.filter_by(classroom_id=classroom.id, day=day). \
            filter(and_(Course.start_week <= week, week <= Course.end_week)). \
            all()
    occupies = []
    for course in courses:
        if course.week_sign == 0 \
            or course.week_sign == 1 and week % 2 == 1 \
            or course.week_sign == 2 and week % 2 == 0:
                occupies.append(course.time)
    return occupies


