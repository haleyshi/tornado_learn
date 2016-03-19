# -*- coding: utf-8 -*-
import os.path
import tornado.web
import tornado.httpserver
import tornado.auth
import tornado.options
import tornado.ioloop
from tornado.options import define, options

from pymongo import MongoClient, DESCENDING

define("port", default=8002, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/edit/([0-9Xx\-]+)", EditHandler),
            (r"/add", EditHandler),
            (r"/delete/([0-9Xx\-]+)", DeleteHandler),
            (r"/blog/([0-9Xx\-]+)", BlogHandler)
        ]

        settings = dict(template_path=os.path.join(os.path.dirname(__file__), "templates"),
                        static_path=os.path.join(os.path.dirname(__file__), "static"),
                        debug=True
                        )

        client = MongoClient("localhost", 27017)
        self.db = client.demo
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        import time
        coll = self.application.db.blog
        blogs = coll.find().sort("id", DESCENDING)
        self.render('index.html', blogs=blogs, time=time)


class EditHandler(tornado.web.RequestHandler):
    def get(self, id=None):
        blog = dict()
        if id is not None:
            coll = self.application.db.blog
            blog = coll.find_one({'id': int(id)})

        self.render('edit.html', blog=blog)

    def post(self, id=None):
        import time

        coll = self.application.db.blog
        blog = dict()

        if id is not None:
            blog = coll.find_one({'id': int(id)})

        blog['title'] = self.get_argument('title', None)
        blog['content'] = self.get_argument('content', None)

        if id is not None:
            coll.save(blog)
        else:
            last = coll.find().sort('id', DESCENDING).limit(1)
            lastone = dict()

            for item in last:
                lastone = item

            if lastone.has_key('id'):
                blog['id'] = int(lastone['id']) + 1
            else:
                blog['id'] = 0
            blog['date'] = int(time.time())
            coll.insert(blog)

        self.redirect('/')


class DeleteHandler(tornado.web.RequestHandler):
    def get(self, id=None):
        if id is not None:
            coll = self.application.db.blog
            blog = coll.remove({'id': int(id)})

        self.redirect('/')


class BlogHandler(tornado.web.RequestHandler):
    def get(self, id=None):
        import time

        if id is not None:
            coll = self.application.db.blog
            blog = coll.find_one({'id': int(id)})
            self.render('blog.html', page_title=blog['title'], blog=blog, time=time)
        else:
            self.redirect('/')


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    print "listen on port:", options.port
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
