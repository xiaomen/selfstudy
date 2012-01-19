# -*- coding: utf-8 -*-

import sys
import string
import datetime
import urllib
import urllib2
import cookielib

import MySQLdb
import lxml.html

reload(sys)
sys.setdefaultencoding('utf8')

class HnuJiaoWu(object):
    
    def __init__(self):
        self.username = self.password = ''
        self.class_region_list = ['00001', '00002', '00003']
        self.class_building_list = []
        self.classroom_list = []
        self.calendar_list = []
        self.semester = ''
        self.operate = ''
        self.cookie_jar = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        urllib2.install_opener(self.opener)
        self.domain = 'http://xjwxt.hnu.cn:8042/student/'
        self.db = ''

    def setinfo(self, username, password, university, semester):
        self.university = university
        self.username = username
        self.password = password
        self.semester = semester
        self.db = MySQLdb.connect(
                host='127.0.0.1',
                user='root',
                passwd='Pa$$w0rd',
                db='selfstudy')

    def getCookie(self):
        self.opener.open(self.domain)
        cookie = cookielib.Cookie(
            version=0,
            name='qzsoftusernamecookie',
            value='Gdyf',
            port=None,
            port_specified=False,
            domain='xjwxt.hnu.cn',
            domain_specified=False,
            domain_initial_dot=False,
            path='/student',
            path_specified=True,
            secure=False,
            expires=None,
            discard=True,
            comment=None,
            comment_url=None,
            rest={'HttpOnly': None},
            rfc2109=False)
        self.cookie_jar.set_cookie(cookie)

    def login(self):
        self.getCookie()
        login_params = {'USERNAME': self.username, 'PASSWORD': self.password}
        self.opener.open(self.domain + 'Logon.do?method=logon',
                urllib.urlencode(login_params))
        self.opener.open(self.domain + 'Logon.do?method=logonBySSO',
                urllib.urlencode({}))
        c = self.db.cursor()
        c.execute('DELETE FROM Class_Occupation')
        c.close()

    def get_school_calendar(self):
        result = self.opener.open(self.domain + 'jiaowu/jxjh/jxrl.do?method=showJxrlAction&xnxqh=' + self.semester)
        s = result.read()
        doc = lxml.html.fromstring(s)
        table = doc.findall('.//body/table')[1]
        year = string.atoi(self.semester.split('-')[0])
        pre_date = datetime.date(year, 1, 1)
        insert_sql = """INSERT INTO School_Calendar(week_no, start_date, university)
                     VALUES (%s, %s, %s)"""
        data_array = []
        for tr in table.xpath('tr'):
            td_list = tr.xpath('td')
            if len(td_list) == 1:
                continue
            td_content_list = [x.text_content().strip() for x in td_list]
            if td_content_list[0] == '':
                continue
            date_str = u'{0}年{1}'.format(year, td_content_list[1])
            cur_date = datetime.datetime.strptime(date_str, u'%Y年%m月%d日').date()
            if cur_date < pre_date:
                year += 1
                cur_date = datetime.date(year, cur_date.month, cur_date.day) 
            week = {'week_no': td_content_list[0], 'start_date': cur_date}
            self.calendar_list.append(week)
            pre_date = cur_date
            dup = (td_content_list[0], cur_date.isoformat(), self.university)
            data_array.append(dup)
        print data_array
        c = self.db.cursor()
        c.execute('DELETE FROM School_Calendar')
        c.executemany(insert_sql, data_array)
        c.close()

    def get_class_building_from_str(self, s):
        if s.endswith(','):
            s = s[:(len(s) - 1)]
        self.class_building_list.extend([{'No.': x.split('#')[0], 'name': x.split('#')[1]} for x in s.split(',')])

    def get_class_building_list(self):

        for x in self.class_region_list:
            result = self.opener.open(self.domain + 'jiaowu/tkgl/tkgl.do?method=queryJxl&xqbh={0}'.format(x))
            s = result.read()
            self.get_class_building_from_str(s)

#        c = self.db.cursor()
#        c.execute('DELETE FROM Class_Building')
#        insert_sql = 'INSERT INTO Class_Building(university, name, building_no) VALUES(%s,%s,%s)'
#        data_array = []
#        for building in self.class_building_list:
#            tup = (self.university, building['name'], building['No.'])
#            data_array.append(tup)
#        c.executemany(insert_sql, data_array)
#        c.close()
 
    def get_classroom_list(self):
        for x in self.class_building_list:
            result = self.opener.open(self.domain + 'jiaowu/tkgl/tkgl.do?method=queryJs&jxqbh=&jxlbh={0}&xqbh='.format(x['No.']))
            s = result.read()
            if s == None or len(s) == 0:
                continue
            if s.endswith(','):
                s = s[:(len(s) - 1)]
            self.classroom_list.extend([{'building': x['No.'], 'No.': y.split('#')[0], 'name': y.split('#')[1]} for y in s.split(',')])

#        c = self.db.cursor()
#        c.execute('DELETE FROM Classroom')
#        insert_sql = 'INSERT INTO Classroom(class_building,room_no,name) VALUES(%s,%s,%s)'
#        data_array = []
#        for cr in self.classroom_list:
#            tup = (cr['building'], cr['No.'], cr['name'])
#            data_array.append(tup)
#        c.executemany(insert_sql, data_array)
#        c.close()

    def get_classroom_schedule(self, classroom_no):
        params = {'zc': '',
                'ywkb': '1',
                'xnxqh': self.semester,
                'jsbh': classroom_no,
                'rxnf': ''}
        req = urllib2.Request(self.domain + 'jiaowu/tkgl/tkgl.do?method=queryKbByJs&type=1', urllib.urlencode(params))
        where1 = self.opener.open(req).read()
        params = {'where1': where1,
                'isOuterJoin': 'false',
                'PageNum': ''}
        c = self.db.cursor()
        page_num = 1
        while True:
            params['PageNum'] = str(page_num)
            req = urllib2.Request(self.domain + 'jiaowu/tkgl/tkgl.do?method=goListKbbysys', urllib.urlencode(params))
            return_str = self.opener.open(req).read()
            doc = lxml.html.fromstring(return_str)
            table = doc.get_element_by_id('mxh')
            if len(table.xpath('tr')) == 0:
                break
            for tr in table.xpath('tr'):
                td_list = tr.xpath('td')
                if len(td_list) <= 1:
                    continue
                td_content_list = [x.text_content() for x in td_list]
                time = td_content_list[10]
                if td_content_list[11].strip() == '':
                    continue
                week_list = td_content_list[11].split(',')
                sign = td_content_list[12]
                insert_sql = """INSERT INTO 
                    Class_Occupation(university,classroom,start_week_no,day_no,class_time,end_week_no,week_sign)
                    VALUES(%s,%s,%s,%s,%s,%s,%s)"""
                day_no = time[0]
                class_time = time[1:]
                data_array = []
                for week in week_list:
                    end_week = start_week = week.split('-')[0]
                    if week.find('-') >= 0:
                        end_week = week.split('-')[1]
                    tup = (self.university, classroom_no, start_week, day_no, class_time, end_week, sign)
                    data_array.append(tup)
                try:
                    c.executemany(insert_sql, data_array)
                except:
                    print classroom_no
                    print data_array
            page_num += 1
        c.close()

    def logout(self):
        self.db.commit()
        self.db.close()
        self.opener.open(self.domain + 'Logon.do?method=logout')


client = HnuJiaoWu()
client.setinfo('Gdyf', 'hd8821842', 'hnu', '2011-2012-1')
client.login()
#client.get_school_calendar()
client.get_class_building_list()
client.get_classroom_list()
for classroom in client.classroom_list:
    client.get_classroom_schedule(classroom['No.'])
client.logout()

