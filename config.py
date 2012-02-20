import os
import web

from sheep.api.statics import static_files
from jinja2 import Environment, FileSystemLoader

jinja_env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),
                            'app/views')),
    extensions=['jinja2.ext.loopcontrols'])
jinja_env.globals.update({})
jinja_env.filters['s_files'] = static_files

db = web.database(dbn='mysql')
