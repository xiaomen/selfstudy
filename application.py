# -*- coding: utf-8 -*-
import json
import datetime
from flask import Flask, redirect, url_for,\
        abort, request, render_template
from functools import wraps

import config
import utils
from models import *
from validate import *
from sheep.api.statics import static_files

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI = config.DATABASE_URI,
    SQLALCHEMY_POOL_SIZE = 1000
)
app.jinja_env.filters['s_files'] = static_files
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

init_db(app)

def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint \
                    .replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator


@app.route('/')
def hello():
    return redirect(url_for('index', uni='hnu'))

@app.route('/<uni>')
@university_validate
def index(uni, quantity=0):
    today = datetime.date.today()
    alldays = '-'.join(map(lambda x: str(x + 1), range(uni.class_quantity)))
    return redirect(url_for('get_buildings',
        uni=uni.no, date=today.isoformat(), classes=alldays))

@app.route('/<uni>/buildings/<date>/<classes>')
@university_validate
@date_validate
@classes_validate
@templated('buildings.html')
def get_buildings(uni, date, classes):
    date = utils.str2date(date)
    occupies = utils.classlist2int(map(lambda x: int(x), classes.split('-')))
    
    occupations = db.session.query(Occupation.classroom_id).\
            filter_by(date = date).\
            filter('occupies.occupies & {0}<>0'.format(occupies))
    free_classrooms = db.session.query(Classroom).\
            filter(~Classroom.id.in_(occupations)).all()
    count = dict()
    for b in uni.buildings:
        count[b.id] = len(filter(lambda x: x.building_id == b.id, free_classrooms))

    return dict(university = uni,
            dates=utils.get_date_filters(),
            query_date=date,
            query_class=classes,
            periods = uni.periods,
            count=count)

