#!/home/pi/brat/flask/bin/python
from flup.server.fcgi import WSGIServer
from app import app
app.debug = True
print "get ready for wsgi"
if __name__ == '__main__':
    WSGIServer(app).run()
