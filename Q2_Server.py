import torndb
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado
import tornado.http1connection
from binascii import hexlify
from tornado.options import define, options
import datetime
import os
import os.path
define("port", default=1104, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_database", default="tickets", help="database name")
define("mysql_user", default="x", help="database user")
define("mysql_password", default="y", help="database password")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            # GET METHOD :
            (r"/signup/([^/]+)/([^/]+)", Signup),
            (r"/login/([^/]+)/([^/]+)", Login),
            (r"/logout/([^/]+)/([^/]+)", Logout),
            (r"/sendticket/([^/]+)/([^/]+)/([^/]+)", SendTicket),
            (r"/getticketcli/([^/]+)", GetTicketClient),
            (r"/closeticket/([^/]+)/([^/]+)", CloseTicket),
            (r"/changeaccess/([^/]+)/([^/]+)/([^/]+)", ChangeAccess),
            (r"/getticketmod/([^/]+)", GetTicketAdmin),
            (r"/restoticketmod/([^/]+)/([^/]+)/([^/]+)", RespondToTicket),
            (r"/changestatus/([^/]+)/([^/]+)/([^/]+)", ChangeStatus),
            # POST METHOD :
            (r"/signup", Signup),
            (r"/login", Login),
            (r"/logout", Logout),
            (r"/sendticket", SendTicket),
            (r"/getticketcli", GetTicketClient),
            (r"/closeticket", CloseTicket),
            (r"/changeaccess", ChangeAccess),
            (r"/getticketmod", GetTicketAdmin),
            (r"/restoticketmod", RespondToTicket),
            (r"/changestatus", ChangeStatus),
        ]
        settings = dict()
        super(Application, self).__init__(handlers, **settings)
        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def check_user(self, user):
        resuser = self.db.get("SELECT * from users where username = %s", user)
        if resuser:
            return True
        else :
            return False

    def check_api(self, api):
        resuser = self.db.get("SELECT * from users where api = %s", api)
        if resuser:
            return True
        else:
            return False

    def check_auth(self,username,password):
        resuser = self.db.get("SELECT * from users where username = %s and password = %s", username,password)
        if resuser:
            return True
        else:
            return False


class DefaultHandler(BaseHandler):
    def get(self, *args):
        self.write({'status': 'Command not found'})

    def post(self, *args, **kwargs):
        self.write({'status': 'Command not found'})


class ChangeAccess(BaseHandler):
    def get(self, *args):
        if self.check_api(args[0]):
            if args[1] == "x" and args[2] == "y":
                self.db.execute("UPDATE users SET isAdmin = %s WHERE api = %s", 1, args[0])
                self.write({'code': '200', 'message': 'You are admin now!'})
            else:
                self.write({'message': 'entered database username or password is not correct'})
        else:
            self.write({'message': 'You are not an authorized party!'})

    def post(self, *args, **kwargs):
        api1 = self.get_argument('api')
        dataBaseUser = self.get_argument('dataBaseUser')
        dataBasePass = self.get_argument('dataBasePass')
        if self.check_api(api1):
            if dataBaseUser == "x" and dataBasePass == "y":
                self.db.execute("UPDATE users SET isAdmin = %s WHERE api = %s", 1, api1)
                self.write({'code': '200', 'message': 'You are admin now!'})
            else:
                self.write({'message': 'entered database username or password is not correct'})
        else:
            self.write({'message': 'You are not an authorized party!'})


class Signup(BaseHandler):
    def get(self, *args):
        if not self.check_user(args[0]):
            api_token = str(hexlify(os.urandom(16)))
            self.db.execute("INSERT INTO users (username, password, api) ""values (%s,%s,%s) ", args[0],
                            args[1], api_token)

            output = {'api': api_token, 'code': '200', 'message': 'successfully signed up'}
            self.write(output)
        else:
            output = {'code': '400', 'message': 'User Exist'}
            self.write(output)

    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        password = self.get_argument('password')
        if not self.check_user(username):
            api_token = str(hexlify(os.urandom(16)))
            self.db.execute("INSERT INTO users (username, password,api) "  "values (%s,%s,%s) ",
                            username, password, api_token)

            output = {'api': api_token,'code': '200', 'message': 'successfully signed up'}
            self.write(output)
        else:
            output = {'code': '400', 'message': 'User Exist'}
            self.write(output)


class Login(BaseHandler):
    def get(self, *args):
        if self.check_auth(args[0], args[1]):
            api_string = self.db.get("SELECT api FROM users where username = %s and password = %s",
                                         args[0], args[1])
            self.write({'api-token': api_string.api, 'code': '200', 'message': 'successfully Logged in'})
        else:
            self.write({'code': '400', 'message': 'entered username or password does not match'})

    def post(self, *args, **kwargs):
        username1 = self.get_argument('username')
        password1 = self.get_argument('password')
        if self.check_auth(username1, password1):
            api_string = self.db.get("SELECT api FROM users where username = %s and password = %s",
                                     username1, password1)
            self.write({'api': api_string.api, 'code': '200', 'message': 'successfully Logged in'})
        else:
            self.write({'code': '400', 'message': 'Can not Log in: entered username or password does not match'})


class Logout(BaseHandler):
    def get(self,*args):
        if self.check_auth(args[0], args[1]):
            self.write({'code': '200', 'message': 'successfully logged out'})
        else:
            self.write({'code': '400', 'status': 'Can not Log out: entered username or password does not match'})

    def post(self, *args, **kwargs):
        username1 = self.get_argument('username')
        password1 = self.get_argument('password')
        if self.check_auth(username1, password1):
            self.write({'code': '200', 'message': 'successfully logged out'})
        else:
            self.write({'code': '400', 'status': 'Can not Log out: entered username or password does not match'})


class SendTicket(BaseHandler):
    def get(self, *args):
        if self.check_api(args[0]):
            mytime = str(datetime.datetime.today())
            self.db.execute("INSERT INTO ticket (api, status, subject, body, sendtime) "
                            "VALUES (%s, %s, %s, %s, %s)",
                            args[0], 'open', args[1], args[2], mytime)
            user = self.db.get("SELECT * FROM ticket where api = %s and sendtime = %s", args[0], mytime)

            user_id = user['id']
            self.write({'code': '200', 'message': 'Ticket sent successfully', 'id': user_id})
        else:
            self.write({'status' : 'You are not and authorized party and so do not have the permission to send tickets!'})

    def post(self, *args, **kwargs):
        api1 = self.get_argument('api')
        status1 = 'open'
        subject1 = self.get_argument('subject')
        body1 = self.get_argument('body')
        if self.check_api(api1):
            date1 = str(datetime.datetime.today())
            self.db.execute("INSERT INTO ticket (api, status, subject, body, sendtime) VALUES (%s,%s,%s,%s,%s)",
                            api1, status1, subject1, body1, date1)
            user = self.db.get("SELECT * FROM ticket where api = %s and sendtime = %s", api1, date1)
            user_id = user['id']
            self.write({'code': '200', 'message': 'Ticket sent successfully', 'id': user_id})
        else:
            self.write({'status': 'You are not and authorized party and so do not have the permission to send tickets!'})


class GetTicketClient(BaseHandler):
    def get(self, *args):
        if self.check_api(args[0]):
            user=self.db.query("SELECT * FROM ticket where api =%s", args[0])
            output = {'tickets': 'There are -{}- Ticket'.format(len(user))}
            for i in range(0, len(user)):
                output['block {}'.format(i)] = user[i]
            self.write(output)
        else:
            self.write({'status': 'You are not an authorized party and do not have the permission to see tickets!'})

    def post(self, *args, **kwargs):
        api1 = self.get_argument('api')
        if self.check_api(api1):
            user = self.db.query("SELECT * FROM ticket where api =%s", api1)
            output = {'code': '200', 'tickets': 'There are -{}- Ticket'.format(len(user))}
            for i in range(0, len(user)):
                output['block {}'.format(i)] = user[i]
            self.write(output)
        else:
            self.write({'status': 'You are not an authorized party and do not have the permission to see tickets!'})


class CloseTicket(BaseHandler):
    def get(self, *args):
        if self.check_api(args[0]):
            user = self.db.query("SELECT * FROM ticket where api = %s and id = %s", args[0], args[1])
            self.db.execute("UPDATE ticket SET status = %s WHERE id = %s and api = %s", 'closed', args[1], args[0])
            if len(user) != 0:
                self.write({'message': 'ticket with id -{}- closed successfully'.format(args[1]), 'code': '200'})
            else:
                self.write({'message': 'The ticket you requested to close does not belong to you!'})
        else:
            self.write({'message': 'You are not an authorized party and do not '
                                  'have the permission to see or modify any tickets!'})

    def post(self, *args, **kwargs):
        api1 = self.get_argument('api')
        id1 = self.get_argument('id')
        if self.check_api(api1):
            user = self.db.query("SELECT * FROM ticket where api = %s and id = %s", api1, id1)
            self.db.execute("UPDATE ticket SET status = %s WHERE id = %s and api = %s", 'closed', id1, api1)
            if len(user) != 0:
                self.write({'message': 'ticket with id -{}- closed successfully'.format(id1), 'code': '200'})
            else:
                self.write({'message': 'The ticket you requested to close does not belong to you!'})
        else:
            self.write({'message': 'You are not an authorized party and do not '
                                  'have the permission to see or modify any tickets!'})


class GetTicketAdmin(BaseHandler):
    def get(self, *args):
        if self.check_api(args[0]):
            user1 = self.db.get("SELECT * FROM users where api = %s", args[0])
            if user1['isAdmin'] == 1:
                user = self.db.query("SELECT * FROM ticket")
                output = {'code': '200', 'tickets': 'There are -{}- Ticket'.format(len(user))}
                for i in range(0, len(user)):
                    output['block {}'.format(i)] = user[i]
                self.write(output)
            else:
                self.write({'code':'400', 'message': 'You are not admin!'})
        else:
            self.write({'code': '400', 'message': 'You are not an authorized party'
                                                  ' and do not have the permission to see tickets!'})

    def post(self, *args, **kwargs):
        api1 = self.get_argument('api')
        if self.check_api(api1):
            user1 = self.db.get("SELECT * FROM users where api = %s", api1)
            if user1['isAdmin'] == 1:
                user = self.db.query("SELECT * FROM ticket where api =%s", api1)
                output = {'code': '200', 'tickets': 'There are -{}- Ticket'.format(len(user))}
                for i in range(0, len(user)):
                    output['block {}'.format(i)] = user[i]
                self.write(output)
            else:
                self.write({'code': '400', 'message': 'You are not admin!'})
        else:
            self.write({'code': '400', 'message': 'You are not an authorized party and do not have '
                                                  'the permission to see tickets!'})


class RespondToTicket(BaseHandler):
    def get(self, *args):
        if self.check_api(args[0]):
            user1 = self.db.get("SELECT * FROM users where api = %s", args[0])
            if user1['isAdmin'] == 1:
                self.db.execute("UPDATE ticket SET answer = %s WHERE id = %s ", args[2], args[1])
                self.write({'message': 'Response to Ticket With id -{}- Sent Successfully'.format(args[1]), 'code': '200'})
            else:
                self.write({'message': 'You are not admin!'})
        else:
            self.write({'message': 'You are not an authorized party and do not have the permission to see tickets!'})

    def post(self, *args, **kwargs):
        api1 = self.get_argument('api')
        id1 = self.get_argument('id')
        answer1 = self.get_argument('answer')
        if self.check_api(api1):
            user1 = self.db.get("SELECT * FROM users where api = %s", api1)
            if user1['isAdmin'] == 1:
                self.db.execute("UPDATE ticket SET answer = %s WHERE id = %s ",  answer1, id1)
                self.write({'message': 'Response to Ticket With id -{}- Sent Successfully'.format(id1), 'code': '200'})
            else:
                self.write({'message': 'You are not admin!'})
        else:
            self.write({'message': 'You are not an authorized party and do not have the permission to see tickets!'})


class ChangeStatus(BaseHandler):
    def get(self, *args):
        if self.check_api(args[0]):
            user1 = self.db.get("SELECT * FROM users where api = %s", args[0])
            if user1['isAdmin'] == 1:
                self.db.execute("UPDATE ticket SET status = %s WHERE id = %s ", args[2], args[1])
                self.write({'message': 'Status Ticket With id -{}- Changed Successfully'.format(args[1]), 'code': '200'})

            else:
                self.write({'message': 'You are not admin!'})
        else:
            self.write({'message': 'You are not an authorized party and do not have the permission to see tickets!'})

    def post(self, *args, **kwargs):
        api1 = self.get_argument('api')
        id1 = self.get_argument('id')
        status1 = self.get_argument('status')
        if self.check_api(api1):
            user1 = self.db.get("SELECT * FROM users where api = %s", api1)
            if user1['isAdmin'] == 1:
                self.db.execute("UPDATE ticket SET status = %s WHERE id = %s ", status1, id1)
                self.write({'message': 'Status Ticket With id -{}- Changed Successfully'.format(id1), 'code': '200'})
            else:
                self.write({'message': 'You are not admin!'})
        else:
            self.write({'message': 'You are not an authorized party and do not have the permission to see tickets!'})


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()