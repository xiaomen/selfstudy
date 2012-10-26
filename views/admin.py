#!/usr/bin/python
#coding:utf-8

import logging

from flask import Blueprint, request, url_for, redirect, render_template
from wtforms import Form, TextField, IntegerField, SelectField, validators

from models import *

logger = logging.getLogger(__name__)

admin = Blueprint('admin', __name__)

week_sign_choices = [(0, u'每周'), (1, u'单周'), (2, u'双周')]

class ClassroomForm(Form):
    name = TextField('name', [validators.Required()])
    capacity = IntegerField('capacity')

class CourseForm(Form):
    start_week = IntegerField('start_week')
    end_week = IntegerField('end_week')
    day = IntegerField('day')
    start_time = IntegerField('start_time', [validators.Required()])
    end_time = IntegerField('end_time', [validators.Required()])
    week_sign = SelectField('week_sign', choices=week_sign_choices, coerce=int)

@admin.route('/', methods=['GET'])
def index():
    buildings = Building.query.all()

    return render_template('admin/index.html', buildings=buildings)

@admin.route('/building/<int:building_id>', methods=['GET', 'POST'])
def building(building_id):
    form = ClassroomForm(request.form)
    if request.method == 'POST' and form.validate():
        building = db.session.query(Building).get(building_id)
        classroom = Classroom(form.name.data, form.capacity.data)
        building.classrooms.append(classroom)
        db.session.add(building)
        db.session.commit()
        logger.info('classroom {0} of building {1} has been added to db.'. \
                format(classroom.id, building.id))
        return redirect(url_for('admin.building', building_id=building_id))

    building = Building.query.get(building_id)
    return render_template('admin/building.html', \
            building=building, form=form)


def get_time(s):
    s = s.split('-')
    if len(s) == 1:
        a = int(s[0])
        b = a
    if len(s) == 2:
        a = int(s[0])
        b = int(s[1])
    return range(a, b + 1)

@admin.route('/classroom/<int:classroom_id>', methods=['GET', 'POST'])
def classroom(classroom_id):
    form = CourseForm(request.form)
    if request.method == 'POST' and form.validate():
        classroom = db.session.query(Classroom).get(classroom_id)
        
        for t in range(form.start_time.data, form.end_time.data + 1):
            course = Course(form.start_week.data, form.end_week.data, \
                    form.day.data, t, form.week_sign.data)
            classroom.courses.append(course)
            db.session.add(classroom)
            logger.info('course {0} of classroom {1} has been added to db.'. \
                    format(course.id, classroom.id))
        db.session.commit()
        return redirect(url_for('admin.classroom', classroom_id=classroom_id))

    classroom = Classroom.query.get(classroom_id)
    return render_template('admin/classroom.html', \
            classroom=classroom, form=form)
