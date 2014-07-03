import tornado.ioloop
import tornado.web
import tornado.options
import os, uuid, cups

# cups object
c = None
# printer name
p = None
# uploaded file name
u_f = None
# middle file path
m_f = None
# print file path
p_f = None

__UPLOADS__ = "static/uploads/"
__TMP__ = "static/tmp/"

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

        p = self.get_argument("printer_selector")
        if p is None:
            self.redirect("/printer")

        fpath = os.path.join(os.path.dirname(__file__), __UPLOADS__ + u_f)

        self.render("confirm.html", filepath=fpath, filename=u_f, printer = p)

    def post(self):
        global c, p, u_f
        if u_f is None:
            self.redirect("/")
        if c is None:
            self.redirect("/printer")
        if p is None:
            self.redirect("/printer")
        fpath = os.path.join(os.path.dirname(__file__), __UPLOADS__ + u_f)

        global m_f, p_f
        m_f = str(uuid.uuid4()) + ".path"
        p_f = str(uuid.uuid4()) + ".rml"
        m_fpath = os.path.join(os.path.dirname(__file__), __TMP__ + m_f)
        p_fpath = os.path.join(os.path.dirname(__file__), __TMP__ + p_f)

        # ( png file path / path file path / error pixels / diameter / offsets / overlap / intensity )
        command = "png_path \"" + fpath + "\" \"" + m_fpath + "\" 1.1 0.25 1 0.5 0.5"
        print command
        ret = os.system(command)
        print ret

        # ( path file path / rml file path / speed / jog / xmin / ymin )
        command = "path_rml \"" + m_fpath + "\" \"" + p_fpath + "\" 100.00 4 1 1 20 20"
        print command
        ret = os.system(command)
        print ret

        print "png file: " + fpath
        print "path file: " + m_fpath
        print "rml file: " + p_fpath

        c.printFile(p, "static/tmp/" + p_f, "rml milling", {})

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
