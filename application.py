import web
import app.controllers

urls = ('/(.*)/', 'redirect',
        '/(.*)/api/buildings.json', 'api.building.buildings',
        '/(.*)/api/building/(.*)/(.*).json', 'api.building.classbuilding',
        '/(.*)/buildings/(.*)/(.*)', 'app.controllers.action.buildings',
        '/(.*)/building/(.*)/(.*)/(.*)', 'app.controllers.action.classbuilding',
        '/(.*)/classroom/(.*)', 'app.controllers.action.room',
        '/(.*)', 'app.controllers.action.index')

class redirect:

    def GET(self, path):
        web.seeother('/' + path)

app = web.application(urls, globals())
wsgi_app = app.wsgifunc()

if __name__ == "__main__":
    app.run()
