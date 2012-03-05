__all__  = ['db', 'University', 'Building', 'Classroom', 'init_db', 'Campus', 'Occupation']

from flaskext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    db.app = app
    db.create_all()

class Classroom(db.Model):
    __tablename__ = 'classrooms'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    building_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    no = db.Column(db.String(20))
    capacity = db.Column(db.Integer)
    seq = db.Column(db.Integer)

    def __init__(self, name, building_id, no, capacity=0, seq=0):
        self.name = name
        self.building_id = building_id
        self.no = no
        self.capacity = capacity
        self.seq = seq

    def to_json_obj(self):
        return dict(class_building=self.building.no,
                name=self.name,
                room_no=self.no)

    def __repr__(self):
        return self.name

class Building(db.Model):
    __tablename__ = 'buildings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    university_id = db.Column(db.Integer)
    campus_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    no = db.Column(db.String(20))
    enabled = db.Column(db.Boolean)
    seq = db.Column(db.Integer)

    classrooms = db.relationship('Classroom',
            foreign_keys=[Classroom.building_id],
            primaryjoin='Classroom.building_id == Building.id',
            backref='building')

    def __init__(self, name, university_id, campus_id, no, enabled=False, seq=0):
        self.name = name
        self.university_id = university_id
        self.campus_id = campus_id
        self.no = no
        self.enabled = enabled
        self.seq = seq

    def to_json_obj(self):
        return dict(name=self.name, building_no=self.no)

class Campus(db.Model):
    __tablename__ = 'campuses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    university_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    no = db.Column(db.String(20))
    seq = db.Column(db.Integer)

    buildings = db.relationship('Building',
            foreign_keys=[Building.campus_id],
            order_by='Building.seq.desc()',
            primaryjoin='and_(Building.campus_id== Campus.id,'
                'Building.enabled==1)',
            backref='campus')

    def __init__(self, name, no, class_quantity):
        self.name = name
        self.no = no
        self.class_quantity = class_quantity

class Period(db.Model):
    __tablename__ = 'periods'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    university_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)

    def __init__(self, name, university_id, start, end):
        self.name = name
        self.university_id = university_id
        self.start = start
        self.end = end

    def query_string(self):
        return '-'.join(map(lambda x: str(x), range(self.start, self.end + 1)))

class University(db.Model):
    __tablename__ = 'universities'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    no = db.Column(db.String(20))
    class_quantity = db.Column(db.Integer)

    periods = db.relationship('Period',
            foreign_keys=[Period.university_id],
            primaryjoin='Period.university_id == University.id',
            backref='university')
    campuses = db.relationship('Campus',
            foreign_keys=[Campus.university_id],
            primaryjoin='Campus.university_id == University.id',
            backref='university')
    buildings = db.relationship('Building',
            order_by='Building.seq.desc()',
            foreign_keys=[Building.university_id],
            primaryjoin='and_(Building.university_id == University.id,'
                'Building.enabled==1)',
            backref='university')

    def __init__(self, name, no, class_quantity):
        self.name = name
        self.no = no
        self.class_quantity = class_quantity
   
class Occupation(db.Model):
    __tablename__ = 'occupies'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    classroom_id = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    occupies = db.Column(db.Integer)

    def __init__(self, classroom_id, date, occupies):
        self.classroom_id = classroom_id
        self.date = date
        self.occupies = occupies
    def __repr__(self):
        return '<Occupation {0} {1} {2}'.format(self.classroom_id, self.date, self.occupies)
