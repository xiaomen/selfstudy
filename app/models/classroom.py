import web

from config import db
from app.models import calendar

def get_classroom_by_id(university, classroom_no):
    return web.listget(db.select('classrooms',
        vars=dict(uni=university, no=classroom_no),
        where='room_no=$no'), 0)

def get_free_time_of_day(university, classroom, date):
    week = calendar.get_calendar(university, date).week_no
    day = date.isoweekday()
    
    occupies = web.listget(
        db.select('occupations',
            vars=dict(uni=university, classroom=classroom.room_no,
                week=week, day=day),
            what='CAST(occupies as unsigned integer) as ocp',
            where='''university=$uni and classroom=$classroom and
                     week=$week and weekday=$day'''), 0).ocp
    return filter(lambda x: occupies & (1 << (x - 1)) == 0, range(1, 12))

#TODO def get_interval_free_time(classroom, start_date, interval_len):

