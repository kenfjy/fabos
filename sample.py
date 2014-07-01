import tornado.ioloop
import tornado.web
import cups

host = "localhost"
c = cups.Connection()
printers = c.getPrinters()

for i in printers:
    print i

print printers[printers.keys()[3]]

# printers[printers.

class MainHandler(tornado.web.RequestHandler):
    def get(self)
        self.write(
