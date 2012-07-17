# -*- coding: utf-8 -*-
import json
import datetime
from flask import Flask, redirect, url_for,\
        abort, request, render_template
from functools import wraps

import utils
from models import *
from validate import *
from sheep.api.statics import static_files

#DATABASE_URI = 'mysql://root:Pa$$w0rd@localhost:3306/selfstudy'
DATABASE_URI = 'mysql://'
LESSON_FORMAT = {
    '1-2-3-4-5-6-7-8-9-10-11' : u'全天', 
    '1-2-3-4' : u'上午', 
    '5-6-7-8' : u'下午', 
    '9-10-11' : u'晚间'
}
app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI = DATABASE_URI,
    SQLALCHEMY_POOL_SIZE = 1000
)

app.jinja_env.filters['s_files'] = static_files
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

init_db(app)

@app.template_filter('format_date')
def format_date(date):
    year, month, day = str(date).split("-")
    return u"%s年%s月%s日" % (year, month, day)

@app.template_filter('format_class')
def format_class(lesson):
    if lesson in LESSON_FORMAT.keys():
        return LESSON_FORMAT[lesson]
    return u", ".join(lesson.split("-")) + u"节课"

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

    return dict(university=uni,
            dates=utils.get_date_filters(),
            query_date=date,
            query_class=classes,
            periods = uni.periods,
            count=count)

@app.route('/<uni>/building/<bld>/<date>/<classes>')
@university_validate
@date_validate
@classes_validate
@templated('building.html')
def get_building(uni, bld, date, classes):
    date = utils.str2date(date)
    occupies = utils.classlist2int(map(lambda x: int(x), classes.split('-')))
    
    building = db.session.query(Building).filter(Building.no == bld).first()
    if building is None:
        abort(404)

    occupations = db.session.query(Classroom.id).\
            filter(Classroom.building_id == building.id).\
            join(Occupation, Classroom.id == Occupation.classroom_id).\
            filter(Occupation.date == date).\
            filter('occupies & %d <> 0' % occupies,)
    free_classrooms = db.session.query(Classroom).\
            filter(Classroom.building_id==building.id).\
            filter(~Classroom.id.in_(occupations)).all()

    return dict(university=uni,
            dates=utils.get_date_filters(),
            query_date=date,
            query_class=classes,
            periods=uni.periods,
            building=building,
            classrooms=free_classrooms)

@app.route('/<uni>/classroom/<clr>')
@university_validate
@classroom_validate
@templated('classroom.html')
def get_classroom(uni, clr):
    dates = utils.get_interval_date(7)
    q = db.session.query(Occupation).\
            filter(Occupation.classroom_id==clr.id)
    occupations = []
    for d in dates:
        result = q.filter(Occupation.date==d[0]).first()
        if result is None:
            occupies = 0
        else:
            occupies = result.occupies
        occupations.append((d[0], d[1],
                            utils.int2classes(occupies, uni.class_quantity)))
    print dir(clr.building.campus.name)
    return dict(university=uni,
            classroom=clr,
            query_date=request.args.get('date', ''),
            query_class=request.args.get('class', ''),
            occupations=occupations)

@app.route('/selfstudy/api/<uni>/building/<bld>/<date>')
@university_validate
@date_validate
def api_query_building(uni, bld, date):
    date = utils.str2date(date)

    building = db.session.query(Building).filter(Building.no == bld).first()
    if building is None:
        abort(404)

    stmt = db.session.query(Occupation.classroom_id, Occupation.occupies).\
            filter(Occupation.date == date).subquery()
    q = db.session.query(Classroom, stmt.c.occupies).\
            outerjoin(stmt, Classroom.id==stmt.c.classroom_id).\
            filter(Classroom.building_id == building.id)
    obj = dict(class_list=[], class_quantity=uni.class_quantity)
    for c, o in q:
        ocp = 0 if o is None else o
        classroom = dict(occupies=ocp,
                occupy_list=utils.int2bitarray(ocp, uni.class_quantity),
                **(c.to_json_obj()))
        obj['class_list'].append(classroom)

    return json.dumps(obj)

@app.route('/selfstudy/api/<uni>/buildings')
@university_validate
def api_get_building_list(uni):
    return json.dumps([x.to_json_obj() for x in uni.buildings])
