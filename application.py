import web
import app.controllers

urls = ('/(.*)/', 'redirect',
        '/(.*)/buildings/(.*)/(.*)', 'app.controllers.action.buildings',
        '/(.*)/classroom/(.*)/(.*)', 'app.controllers.action.room')

class redirect:
    def GET(self, path):
        web.seeother('/' + path)

app = web.application(urls, globals())
wsgi_app = app.wsgifunc()

if __name__ == "__main__":
    app.run()
