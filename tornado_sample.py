import tornado.ioloop
import tornado.web
import tornado.options
import os, uuid, cups

c = None
f = None
p = None

__UPLOADS__ = "static/uploads/"

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", FileHandler),
            (r"/printer.*", PrinterHandler),
            (r"/confirm.*", ConfirmHandler),
            (r"/printfile.*", PrintFileHandler),
            (r"/uploads/^(.*)",tornado.web.StaticFileHandler, {"path": "./uploads"},),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            )
        tornado.web.Application.__init__(self, handlers, **settings)

# handles files
class FileHandler(tornado.web.RequestHandler):
    def get(self):
        global f;
        self.render("upload.html", filename = f)
    def post(self):
        global f;
        self.render("upload.html", filename = f)

# handles printer check
class PrinterHandler(tornado.web.RequestHandler):
    def get(self):
        global c, f, p
        if f is None: 
            self.redirect("/")
        else:
            if c is None:
                c = cups.Connection()
            printers = c.getPrinters()
            
            self.render("printer.html", printers=printers, filename = f, sel_printer=p)
    def post(self):
        global c, f, p
        fileinfo = self.request.files['up_file'][0]
        print "fileinfo is ", fileinfo
        fname = fileinfo['filename']
        extn = os.path.splitext(fname)[1]
        cname = str(uuid.uuid4()) + extn
        fh = open(__UPLOADS__ + cname, 'w')
        fh.write(fileinfo['body'])
        f = cname

        fpath = os.path.join(os.path.dirname(__file__), __UPLOADS__ + f)
        print fpath

        if c is None:
            c = cups.Connection()
        printers = c.getPrinters()

        self.render("printer.html", printers=printers, filename = f, sel_printer=p)

# handles printing confirmation
class ConfirmHandler(tornado.web.RequestHandler):
    def get(self):
        global c, f, p
        if f is None:
            self.redirect("/")
        if c is None:
            self.redirect("/printer")
        if p is None:
            self.redirect("/printer")

        self.write("you have chosen " + p)

    def post(self):
        global c, f, p
        if f is None:
            self.redirect("/")
        if c is None:
            self.redirect("/printer")

        p = self.get_argument("printer_selector")
        if p is None:
            self.redirect("/printer")

        self.write("you have chosen " + p)

# handles printing confirmation
class PrintFileHandler(tornado.web.RequestHandler):
    def get(self):
        global c, f, p
        if f is None:
            self.redirect("/")
        if c is None:
            self.redirect("/printer")
        if p is None:
            self.redirect("/printer")

        c.printFile(p, "static/uploads/" + f, "rml milling", {})

    def post(self):
        global c, f, p
        if f is None:
            self.redirect("/")
        if c is None:
            self.redirect("/printer")
        if p is None:
            self.redirect("/printer")

        c.printFile(p, "static/uploads/" + f, "rml milling", {})

# class PrintHandler(tornado.web.RequestHandler):
#     def get(self):

def main():
    global c, f, p
    c = None
    f = None
    p = None

    # test for directory existance
    uppath = __UPLOADS__ + "sample.txt"
    uppath = os.path.dirname(uppath)
    print "PATH: " + uppath
    if not os.path.exists(uppath):
        os.makedirs(uppath)

    cups.setServer("localhost")
    application = Application()
    application.listen(8080, '0.0.0.0')
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
