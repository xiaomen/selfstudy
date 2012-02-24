import json

from app.models import university
from app.models import building
from app.models import calendar
from app.helpers import utils

class buildings:

    def GET(self, uni_param):
        return json.dumps(building.get_buildings(uni_param))

class classbuilding:

    def GET(self, uni_param, building_no, date_param):
        uni = university.get_university_by_no(uni_param)
        date = utils.str2date(date_param)
        bld = building.get_building_by_id(uni_param, building_no)
        class_list = building.get_free_buildings_detail(uni_param, bld, date)
        max_class_no = calendar.get_max_class_no(uni_param)
        return json.dumps(dict(class_quantity=max_class_no,
            class_list=class_list))
