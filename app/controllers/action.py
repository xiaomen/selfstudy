from config import jinja_env

from app.models import university
from app.models import building
from app.models import classroom

from app.helpers import utils

class buildings:

    def GET(self, uni_param, date_param, class_param):
        uni = university.get_university_by_no(uni_param)
        date = utils.str2date(date_param)
        class_list = map(lambda x: int(x), class_param.split('-'))

        buildings = building.get_free_buildings(uni_param, date, class_list)
        #return jinja_env.get_template('buildings.html').render()
        return buildings

class room:

    def GET(self, uni_param, room_no, date_param):
        uni = university.get_university_by_no(uni_param)
        date = utils.str2date(date_param)
        room = classroom.get_classroom_by_id(uni_param, room_no)

        free_list = classroom.get_free_time_of_day(uni_param, room, date)
        return free_list
