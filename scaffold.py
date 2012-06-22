#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import os
import logging
import uuid

import tornado.options
import tornado.ioloop
import tornado.web
import tornado.template
import tornado.database


class ScaffoldHandler(tornado.web.RequestHandler):
    TABLE = 'users'
    def get(self):
        view = self.get_argument("_view", "list").lower()
        if view == 'list':
            self.write("<a href='?_view=create'>Create</a>")
            records = conn.query("SELECT * FROM " + self.TABLE)
            if not records:
                self.finish()
                return

            self.write("<table>")
            self.write("<tr>")
            for i in records[0].keys():
                self.write("<td>%s</td>" % i)
            self.write("<td>ACTION</td>")
            self.write("</tr>")

            for i in records:
                self.write("<tr>")
                self.write("".join(["<td>%s</td>" % v for v in i.values()]))
                self.write("<td><a href='?_view=read&_id=%s'>Edit</a></td>"% i["id"])
                self.write("</tr>")
            self.write("</table>")

        elif view == 'read':
            id = self.get_argument("_id")
            records = conn.query("SELECT * FROM " + self.TABLE+" WHERE id=%s", id)
            input_tag = "<label>%s</label><br /><input type='text' name='%s' value='%s' /><br />"
            self.write("<a href='?_view=list'>Back</a> ")
            self.write("<a href='?_view=create'>Create</a>")
            for i in records:
                self.write("<form method='POST'>")
                self.write(" ".join([input_tag % (a,a,b) for a,b in i.iteritems()]))
                self.write("<input type='submit' name='_action' value='Update' />")
                self.write("<input type='submit' name='_action' value='Delete' />")
                self.write("</form>")

        elif view == 'create':
            fields = [i.strip().split()[0].strip('`') for i in conn.query("SHOW CREATE TABLE "+ self.TABLE)[0]['Create Table'].split('\n')[1:-1] if i.strip().startswith('`')]
            input_tag = "<label>%s</label><br /><input type='text' name='%s' value='' /><br />"
            self.write("<a href='?_view=list'>Back</a>")
            self.write("<form method='POST'>")
            self.write(" ".join([input_tag % (i, i) for i in fields if i != "id"]))
            self.write("<input type='submit' name='_action' value='Create' />")
            self.write("</form>")

    def post(self):
        action = self.get_argument("_action", "").lower()
        if action == 'create':
            fields = [i for i in self.request.arguments if not i.startswith('_')]
            values = [self.get_argument(i) for i in fields]
            sql = "INSERT INTO "+self.TABLE+" ("+','.join(fields)+") VALUES("+",".join(["%s"]*len(values))+")"
            print sql, values
            conn.execute(sql, *values)

        elif action == 'delete':
            sql = "DELETE FROM "+self.TABLE+" WHERE id=%s"
            conn.execute(sql, self.get_argument('_id'))

        elif action == 'update':
            fields = [i for i in self.request.arguments if not i.startswith('_')]
            values = [self.get_argument(i) for i in fields] + [self.get_argument('_id')]
            sql = "UPDATE "+self.TABLE+" SET "+', '.join([i+"=%s" for i in fields])+" WHERE id=%s"
            print sql
            conn.execute(sql, *values)

        self.write("<a href='?_action=list'>Back</a>")


settings = {
    #"xsrf_cookies": True,
    "static_path": os.path.join(os.path.dirname(__file__), "static/"),
    "cookie_secret": "000000000000000000000000000000000000000000000",
    "login_url": "/",
    "debug": True,
}

try:
    import tornado.database

    if settings["debug"]:
        conn = tornado.database.Connection("127.0.0.1", "test", "root", "root")
    else:
        conn = tornado.database.Connection("/var/run/mysqld/mysqld.sock", "test", "root", "root")
except:
    pass


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", ScaffoldHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path'], default_filename='index.html')),
    ], **settings)

    tornado.options.parse_command_line()
    application.listen(int(sys.argv[1]))
    tornado.ioloop.IOLoop.instance().start()
