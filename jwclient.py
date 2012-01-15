import sys

import urllib
import urllib2
import cookielib

import lxml.html

class HnuJiaoWu(object):

    def __init__(self):
        self.username = self.password = ''
        self.class_region_list = ['00001', '00002', '00003']
        self.class_building_list = []
        self.classroom_list = []
        self.semester = ''
        self.operate = ''
        self.cookie_jar = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        urllib2.install_opener(self.opener)
        self.domain = 'http://xjwxt.hnu.cn:8042/student/'

    def setinfo(self, username, password, semester):
        self.username = username
        self.password = password
        self.semester = semester

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

    def get_class_building_from_str(self, s):
        if s.endswith(','):
            s = s[:(len(s) - 1)]
        self.class_building_list.extend([{'No.': x.split('#')[0], 'name': x.split('#')[1]} for x in s.split(',')])

    def get_class_building_list(self):
        for x in self.class_region_list:
            result = self.opener.open(self.domain + 'jiaowu/tkgl/tkgl.do?method=queryJxl&xqbh={0}'.format(x))
            s = result.read()
            self.get_class_building_from_str(s)
 
    def get_classroom_list(self):
        for x in self.class_building_list:
            result = self.opener.open(self.domain + 'jiaowu/tkgl/tkgl.do?method=queryJs&jxqbh=&jxlbh={0}&xqbh='.format(x['No.']))
            s = result.read()
            if s == None or len(s) == 0:
                continue
            if s.endswith(','):
                s = s[:(len(s) - 1)]
            self.classroom_list.extend([{'building': x['No.'], 'No.': y.split('#')[0], 'name': y.split('#')[1]} for y in s.split(',')])

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
        page_num = 1
        while True:
            params['PageNum'] = str(page_num)
            req = urllib2.Request(self.domain + 'jiaowu/tkgl/tkgl.do?method=goListKbbysys', urllib.urlencode(params))
            return_str = self.opener.open(req).read()
            doc = lxml.html.fromstring(return_str)
            table = doc.get_element_by_id('mxh')
            if len(table.xpath('tr')) == 0:
                break
            #for tr in table.xpath('tr'):
            #    print u'###{0}###'.format(tr.text_content())
            page_num += 1

        print page_num

    def logout(self):
        self.opener.open(self.domain + 'Logon.do?method=logout')


client = HnuJiaoWu()
client.setinfo('Gdyf', 'hd8821842', '2011-2012-1')
client.login()
client.get_class_building_list()
client.get_classroom_list()
for cr in client.classroom_list:
    
    print cr['No.'] + '   ' + cr['name']
    try:
        client.get_classroom_schedule(cr['No.'])
    except:
        sys.exit()
client.logout()
