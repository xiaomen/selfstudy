import config

from config import jinja_env

class index:
    def GET(self, university):
        print university

        return jinja_env.get_template('index.html').render(
                university=university)
