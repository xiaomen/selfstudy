__all__ = ['university_validate', 'date_validate', 'classes_validate',
           'classroom_validate']

import datetime

from flask import abort 
from functools import wraps

from models import *
import utils

def university_validate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'uni' in kwargs:
            u = University.query.filter_by(no=kwargs['uni']).first()
            if u == None:
                abort(404)
            kwargs['uni'] = u
        return f(*args, **kwargs)
    return decorated_function

def date_validate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'date' in kwargs:
            today = datetime.date.today()
            dates = map(lambda x: x.isoformat(), utils.get_select_date_list(3))
            if not kwargs['date'] in dates:
                abort(404)
        return f(*args, **kwargs)
    return decorated_function

def classes_validate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'classes' in kwargs:
            q = kwargs['uni'].class_quantity
            s = set(kwargs['classes'].split('-'))
            if not s <= set(map(lambda x: str(x + 1), range(q))):
                abort(404)
        return f(*args, **kwargs)
    return decorated_function

def classroom_validate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'clr' in kwargs:
            c = Classroom.query.filter_by(no=kwargs['clr']).first()
            if c == None:
                abort(404)
            kwargs['clr'] = c
        return f(*args, **kwargs)
    return decorated_function
