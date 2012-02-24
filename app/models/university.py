import web
from config import db

def get_university_by_no(no):
    return web.listget(
            db.select('universities', vars=dict(no=no),
                where='short_name=$no'), 0)
