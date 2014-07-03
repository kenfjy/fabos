import tornado.ioloop
import tornado.web
import tornado.options
import os, uuid, cups

# cups object
c = None
# printer name
p = None
# uploaded file path
u_f = None
# middle file path
m_f = None
# print file path
p_f = None

__UPLOADS__ = "static/uploads/"
__TMP__ = "static/tmp"

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", FileHandler),
            (r"/printer.*", PrinterHandler),
            (r"/confirm.*", ConfirmHandler),
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
        global u_f;
        self.render("upload.html", filename = u_f)
        
    def post(self):
        global u_f;
        self.render("upload.html", filename = u_f)

# handles printer check
class PrinterHandler(tornado.web.RequestHandler):
    def get(self):
        global c, p, u_f
        if u_f is None: 
            self.redirect("/")

        if c is None:
            c = cups.Connection()
        printers = c.getPrinters()
        
        self.render("printer.html", printers=printers, sel_printer=p, filename = u_f)

    def post(self):
        global c, p, u_f
        fileinfo = self.request.files['up_file'][0]
        print "fileinfo is ", fileinfo
        fname = fileinfo['filename']
        extn = os.path.splitext(fname)[1]
        cname = str(uuid.uuid4()) + extn
        fh = open(__UPLOADS__ + cname, 'w')
        fh.write(fileinfo['body'])
        u_f = cname

        fpath = os.path.join(os.path.dirname(__file__), __UPLOADS__ + u_f)
        print fpath

        if c is None:
            c = cups.Connection()
        printers = c.getPrinters()

        self.render("printer.html", printers=printers, sel_printer=p, filename = u_f)

# handles printing confirmation
class ConfirmHandler(tornado.web.RequestHandler):
    def get(self):
        global c, p, u_f
        if u_f is None:
            self.redirect("/")
        if c is None:
            self.redirect("/printer")
        if p is None:
            self.redirect("/printer")

        fpath = os.path.join(os.path.dirname(__file__), __UPLOADS__ + u_f)
        print fpath

        c.printFile(p, "static/uploads/" + u_f, "rml milling", {})

    def post(self):
        global c, p, u_f
        if u_f is None:
            self.redirect("/")
        if c is None:
            self.redirect("/printer")

        p = self.get_argument("printer_selector")
        if p is None:
            self.redirect("/printer")

        fpath = os.path.join(os.path.dirname(__file__), __UPLOADS__ + u_f)

        self.render("confirm.html", filepath=fpath, filename=u_f, printer = p)

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
    if not os.path.exists(uppath):
        print "making directories at " + uppath
        os.makedirs(uppath)

    temppath = __TMP__ + "sample.txt"
    temppath = os.path.dirname(temppath)
    if not os.path.exists(temppath):
        print "making directories at " + temppath
        os.makedirs(temppath)

    cups.setServer("localhost")
    application = Application()
    application.listen(8080, '0.0.0.0')
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
