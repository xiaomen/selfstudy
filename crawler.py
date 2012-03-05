# -*- coding: utf-8 -*-
import sys
import urllib
import urllib2
import cookielib
import datetime
from datetime import timedelta
from flask import Flask
import lxml.html

import config
from models import *

reload(sys)
sys.setdefaultencoding('utf8')

cookie = cookielib.Cookie(
    version=0, name='qzsoftusernamecookie', value='Gdyf', port=None,
    port_specified=False, domain='xjwxt.hnu.cn', domain_specified=False,
    domain_initial_dot=False, path='/student', path_specified=True,
    secure=False, expires=None, discard=True, comment=None,
    comment_url=None, rest={'HttpOnly': None}, rfc2109=False
)

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI=config.DATABASE_URI,
    SQLALCHEMY_POOL_SIZE = 1000
)

init_db(app)

hnu = University.query.filter_by(no='hnu').first()
print len(hnu.buildings[1].classrooms)

class Client:
    
    def __init__(self, uni, username, password, semester):
        self.university = uni
        self.username = username
        self.password = password
        self.semester = semester
        if semester.split('-')[2] == '1':
            self.year = int(semester.split('-')[0])
        else:
            self.year = int(semester.split('-')[1])
        
        self.domain = 'http://xjwxt.hnu.cn:8042/student/'
        self.cookie_jar = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        urllib2.install_opener(self.opener)

        self.calendars = []
        self.buildings = []
        self.classrooms = []
        self.occupies = []

    def get_cookie(self):
        self.opener.open(self.domain)
        self.cookie_jar.set_cookie(cookie)

    
    def get_calendar_from_html(self, tds):
        contents = map(lambda x: x.text_content().strip(), tds)
        if len(contents[0]) == 0:
            return None
        week = int(contents[0])
        date_str = u'{0}年{1}'.format(self.year, contents[1])
        date = datetime.datetime.strptime(date_str, u'%Y年%m月%d日').date()

        return dict(week=week, date=date)

    def get_calendars(self):
        url = 'jiaowu/jxjh/jxrl.do?method=showJxrlAction&xnxqh='
        result = self.opener.open(self.domain + url + self.semester)
        s = result.read()
        doc = lxml.html.fromstring(s)
        table = doc.findall('.//body/table')[1]
        pre_date = datetime.date(self.year, 1, 1)
        for tr in table.xpath('tr'):
            tds = tr.xpath('td')
            if len(tds) == 1:
                continue
            calendar = self.get_calendar_from_html(tds)
            if calendar == None:
                continue
            if len(self.calendars) > 0 \
            and calendar['date'] < self.calendars[-1]['date']:
                calendar['date'] = datetime.date(
                        self.year + 1,
                        calendar['date'].month,
                        calendar['date'].day
                )
            self.calendars.append(calendar)


    def login(self):
        self.get_cookie()
        p = dict(USERNAME=self.username, PASSWORD=self.password)
        self.opener.open(self.domain + 'Logon.do?method=logon',
                urllib.urlencode(p))
        self.opener.open(self.domain + 'Logon.do?method=logonBySSO',
                urllib.urlencode({}))

        self.get_calendars()

    def get_buildings_from_server(self):
        def f(x, campus_id):
            return Building(x.split('#')[1],
                            self.university.id,
                            campus_id,
                            x.split('#')[0])
            
        for c in hnu.campuses:
            url = 'jiaowu/tkgl/tkgl.do?method=queryJxl&xqbh={0}'.format(c.no)
            result = self.opener.open(self.domain + url)
            s = result.read()
            if s.endswith(','):
                s = s[:len(s) - 1]
            self.buildings.extend(map(lambda x: f(x, c.id), s.split(','))) 

        b = Building(u'综合楼', self.university.id, 1, 'ENU7KRJxQw', True)
        self.buildings.append(b)


    def get_classrooms_from_server(self):
        def f(x, building_id):
            print x
            no = x.split('#')[0]
            name = x.split('#')[1]
            index = name.find('[')
            capacity = name[index + 1:-1]
            if capacity.isdigit():
                capacity = int(capacity)
            else:
                capacity = 0
            return Classroom(name[:index], building_id, no, capacity)

        url = 'jiaowu/tkgl/tkgl.do?method=queryJs&jxqbh=&jxlbh={0}&xqbh='
        for b in hnu.buildings:
            if not b.enabled:
                continue
            result = self.opener.open(self.domain + url.format(b.no))
            s = result.read()
            if s == None or len(s) == 0:
                continue
            if s.endswith(','):
                s = s[:len(s) - 1]
            self.classrooms.extend(map(lambda x: f(x, b.id), s.split(',')))
            
        
    def initialize_occupies(self):
        start = self.calendars[0]['date']
        weeks = len(self.calendars)
        for b in hnu.buildings:
            for c in b.classrooms:
                for delta in range(weeks * 7):
                    occupy = Occupation(c.id, start + timedelta(days=delta), 0)
                    db.session.add(occupy)
        db.session.commit()

    def get_occupies_from_html(self, tr, classroom):
        tds = tr.xpath('td')
        if len(tds) <= 1:
            return None
        contents = map(lambda x: x.text_content().strip(), tds)
        if contents[11] == '':
            return None
        time = contents[10]
        weeks = contents[11].split(',')
        sign = contents[12]
        day = int(contents[10][0])
        occupation = self.classes2int(contents[10][1:])

        for week in weeks:
            end = start = int(week.split('-')[0])
            if '-' in week:
                end = int(week.split('-')[1])
        for i in self.interval2list(start, end, sign):
            date = self.week2date(i, day)
            o_list = filter(lambda x: x.date == date and x.classroom_id == classroom.id, self.occupies)
            if len(o_list) == 0:
                o = Occupation(classroom.id, self.week2date(i, day), occupation)
                self.occupies.append(o)
            else:
                o_list[0].occupies |= occupation
        
    def week2date(self, week, day):
        calendar = self.calendars[week - 1]
        date = calendar['date'] + timedelta(days=day % 7)
        return date

    def interval2list(self, start, end, sign):
        if sign == '1':
            f = lambda x: True
        elif sign == '2':
            f = lambda x: x % 2 != 0
        else:
            f = lambda x: x % 2 == 0
        return filter(f, range(start, end))
            
    def classes2int(self, classes):
        ret = 0
        while len(classes) > 0:
            no = int(classes[0:2]) - 1
            ret |= (1 << no)
            classes = classes[2:]
        return ret

    def get_classrooms_occupies(self, classroom):
        print classroom.name + ' ' + classroom.no
        params = {'zc': '', 'ywkb': '1', 'xnxqh': self.semester,
                  'jsbh': classroom.no, 'rxnf': ''}
        url = 'jiaowu/tkgl/tkgl.do?method=queryKbByJs&type=1'
        req = urllib2.Request(self.domain + url, urllib.urlencode(params))
        where1 = self.opener.open(req).read()
        params = {'where1': where1,
                  'isOuterJoin': 'false',
                  'PageNum': ''}
        page_num = 1
        while True:
            params['PageNum'] = str(page_num)
            url = self.domain + 'jiaowu/tkgl/tkgl.do?method=goListKbbysys'
            req = urllib2.Request(url, urllib.urlencode(params))
            result = self.opener.open(req).read()
            doc = lxml.html.fromstring(result)
            table = doc.get_element_by_id('mxh')
            if len(table.xpath('tr')) == 0:
                break
            for tr in table.xpath('tr'):
                self.get_occupies_from_html(tr, classroom)
            page_num += 1 

    def get_occupies(self):
        for b in hnu.buildings:
            if not b.enabled:
                continue
            for c in b.classrooms:
                self.get_classrooms_occupies(c)

    def logout(self):
        self.opener.open(self.domain + 'Logon.do?method=logout')

client = Client(hnu, 'Gdyf', 'hd8821842', '2011-2012-2')
client.login()
#client.get_classrooms_occupies(Classroom.query.filter_by(no='AOYaDZPYLu').first())
client.get_occupies()
client.logout()

for o in client.occupies:
    db.session.add(o)
db.session.commit()
