import web

from config import db

def get_calendar(university, date):
    return web.listget(
            db.select('calendars', vars=dict(name=university, date=date),
                where='university=$name and datediff($date, start_date)<7',
                order='week_no ASC'), 0)
