from flask import Flask

import config
import utils
from models import *
from sheep.api.statics import static_files

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI = config.DATABASE_URI,
    SQLALCHEMY_POOL_SIZE = 1000
)
app.jinja_env.filters['s_files'] = static_files

init_db(app)

@app.route('/')
def hello():
    return 'HelloWorld'

@app.route('/<uni>/buildings/<date>/<classes>')
def get_buildings(uni, date, classes):
    date = utils.str2date(date_param)
    classes = map(lambda x: int(x), classes.split('-'))
