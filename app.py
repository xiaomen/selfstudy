import web
import controllers

urls = ('/(.*)/', 'controllers.index.index')

app = web.application(urls, globals())
wsgi_app = app.wsgifunc()

if __name__ == "__main__":
    app.run()
