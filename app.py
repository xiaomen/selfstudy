# -*- coding: utf-8 -*-
import json
import datetime
from flask import Flask, redirect, url_for,\
        abort, request, render_template, g
from functools import wraps
from werkzeug.useragents import UserAgent

import utils
import config

from views.admin import admin
from models import *
from validate import *

from sheep.api.statics import static_files
from sheep.api.sessions import SessionMiddleware, \
    FilesystemSessionStore
from sheep.api.users import *

LESSON_FORMAT = {
    '1-2-3-4-5-6-7-8-9-10-11' : u'全天', 
    '1-2-3-4' : u'上午', 
    '5-6-7-8' : u'下午', 
    '9-10-11' : u'晚间'
}

app = Flask(__name__)
app.debug = config.DEBUG

app.config.update(
    SQLALCHEMY_DATABASE_URI = config.DATABASE_URI,
    SQLALCHEMY_POOL_SIZE = 100,
    SQLALCHEMY_POOL_TIMEOUT = 10,
    SQLALCHEMY_POOL_RECYCLE = 3600,
    SESSION_COOKIE_DOMAIN = config.SESSION_COOKIE_DOMAIN
)

app.jinja_env.filters['s_files'] = static_files
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.jinja_env.globals['generate_user_url'] = generate_user_url
app.jinja_env.globals['generate_login_url'] = generate_login_url
app.jinja_env.globals['generate_logout_url'] = generate_logout_url
app.jinja_env.globals['generate_register_url'] = generate_register_url
app.jinja_env.globals['generate_mail_url'] = generate_mail_url

app.register_blueprint(admin, url_prefix='/admin')

app.wsgi_app = SessionMiddleware(app.wsgi_app, \
        FilesystemSessionStore(), \
        cookie_name=config.SESSION_KEY, cookie_path='/', \
        cookie_domain=config.SESSION_COOKIE_DOMAIN)

init_db(app)

@app.template_filter('format_date')
def format_date(select):
    year, month, day = map(int, str(select).split("-"))
    select = datetime.datetime(year, month, day).date()
    today = datetime.datetime.now()
    delta = select - today.date()
    if delta.days == 0:
        return u"今日"
    elif delta.days == 1:
        return u"明日"
    elif delta.days == 2:
        return u"后日"
    return u"%s年<strong>%d</strong>月<strong>%d</strong>日" % (select.year, select.month, select.day)

@app.template_filter('format_class')
def format_class(lesson):
    if lesson in LESSON_FORMAT.keys():
        return LESSON_FORMAT[lesson]
    return u", ".join(lesson.split("-")) + u"节课"

@app.template_filter('check_class')
def check_date(cls, check_val):
    return 'id="lesson-selected"' if cls == check_val else "" 

def get_ua(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        ua_string = request.headers.get('User-Agent')
        if not ua_string:
            return method(*args, **kwargs)
        ua = UserAgent(request.headers.get('User-Agent'))
        if ua.browser == 'msie':
            try:
                if int(float(ua.version)) < 8:
                    return render_template("noie.html")
            except:
                return render_template("noie.html")
        return method(*args, **kwargs) 
    return wrapper

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
            ua_string = request.headers.get('User-Agent')
            if not ua_string:
                return render_template("mobile/" + template_name, **ctx) 
            ua = UserAgent(ua_string)
            if ua.platform and ua.platform.lower() in ["android", "iphone"]:
                return render_template("mobile/" + template_name, **ctx)
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator


@app.route('/')
def hello():
    return u'自习室升级中，敬请期待'

@app.route('/<uni>')
@university_validate
def index(uni, quantity=0):
    return u'自习室升级中，敬请期待'

@app.before_request
def before_request():
    g.session = request.environ['xiaomen.session']
    g.current_user = get_current_user(g.session)
    if g.current_user:
        g.unread_mail_count = lambda: get_unread_mail_count(g.current_user.uid)
