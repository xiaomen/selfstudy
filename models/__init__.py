from datetime import datetime
from flaskext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    db.app = app
    db.create_all()

class University(db.Model):
    __tablename__ = 'university'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    no = db.Column(db.String(20))
    class_quantity = db.Column(db.Integer)
    start_date = db.Column(db.Date)

    periods = db.relationship('Period', backref='university', lazy='dynamic')
    campuses = db.relationship('Campus', backref='unisersity', lazy='dynamic')

    def __init__(self, name, no, class_quantity, start_date):
        self.name = name
        self.no = no
        self.class_quantity = class_quantity
        self.start_date = start_date

class Period(db.Model):
    __tablename__ = 'period'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'))
    name = db.Column(db.String(50))
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)

    def __init__(self, name, university_id, start, end):
        self.name = name
        self.university_id = university_id
        self.start = start
        self.end = end

class Campus(db.Model):
    __tablename__ = 'campus'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'))
    name = db.Column(db.String(50))
    seq = db.Column(db.Integer)

    buildings = db.relationship('Building', backref='campus', lazy='dynamic')

    def __init__(self, name, seq=0):
        self.name = name
        self.seq = seq

class Building(db.Model):
    __tablename__ = 'building'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'))
    name = db.Column(db.String(50))
    seq = db.Column(db.Integer)

    classrooms = db.relationship('Classroom', backref='building', lazy='dynamic')

    def __init__(self, name, seq=0):
        self.name = name
        self.seq = seq

class Classroom(db.Model):
    __tablename__ = 'classroom'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'))
    name = db.Column(db.String(50))
    capacity = db.Column(db.Integer)
    seq = db.Column(db.Integer)

    courses = db.relationship('Course', backref='classroom', lazy='dynamic')

    def __init__(self, name, capacity=0, seq=0):
        self.name = name
        self.capacity = capacity
        self.seq = seq

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'))
    start_week = db.Column(db.Integer)
    end_week = db.Column(db.Integer)
    day = db.Column(db.Integer)
    time = db.Column(db.Integer)
    week_sign = db.Column(db.Integer)

    def __init__(self, start_week, end_week, day, time, week_sign):
        self.start_week = start_week
        self.end_week = end_week
        self.day = day
        self.time = time
        self.week_sign = week_sign

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, nullable=False, index=True)
    classroom_id = db.Column(db.Integer, nullable=False, index=True)
    occupy = db.Column(db.Boolean)
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, uid, classroom_id, occupy):
        self.uid = uid
        self.classroom_id = classroom_id
        self.occupy = occupy

    @staticmethod
    def create(uid, classroom_id, occupy=True):
        f = Feedback(uid, classroom_id, occupy)
        db.session.add(f)
        db.session.commit()
