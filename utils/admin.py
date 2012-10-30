from functools import wraps
from flask import g, url_for, redirect, request, abort
from config import ACCOUNT_LOGIN
from urllib import quote
from models import Admin

def login_required(next=None, need=True, *args, **kwargs):
    def _login_required(f):
        @wraps(f)
        def _(*args, **kwargs):
            if (need and not g.current_user) or \
                    (not need and g.current_user):
                if next:
                    if next != ACCOUNT_LOGIN:
                        url = next
                    else:
                        url = '{0}?{1}={2}'.format(next, 'redirect', quote(request.url))
                    return redirect(url)
                return redirect('/')
            if g.current_user:
                admin = Admin.query.filter_by(uid=g.current_user.uid).first()
                if not admin:
                    abort(403)
            return f(*args, **kwargs)
        return _
    return _login_required

def get_time(s):
    s = s.split('-')
    if len(s) == 1:
        a = int(s[0])
        b = a
    if len(s) == 2:
        a = int(s[0])
        b = int(s[1])
    return range(a, b + 1)

