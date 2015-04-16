from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.utils.importlib import import_module
import os
import django
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, define, options
from tornado.web import Application, FallbackHandler, RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.wsgi import WSGIContainer

define('host', type=str, default="localhost")
define('port', type=int, default=8080)


class HelloTornado(RequestHandler):
    def get(self):
        self.write('Hello from Tornado')


class WSHandler(WebSocketHandler):
    def open(self):
        # self.current_user = self.get_django_current_user()

        session_key = self.get_cookie(settings)
        session_engine = import_module(settings.SESSION_ENGINE)
        session = session_engine.SessionStore(session_key)

        # try:
        #     user_id = session['_auth_user_id']
        #     user_name = User.objects.get(id=self.user_id).username
        #     print 'userid: {0}, username: {1}'.format(user_id, user_name)
        # except (KeyError, User.DoesNotExist):
        #     self.close()

    def on_message(self, message):
        pass

    def on_close(self):
        pass

    # def get_django_current_user(self):
    #     class Dummy(object):
    #         pass
    #     django_request = Dummy()
    #     django_request.session = self.get_django_session()
    #
    #     user = get_user(django_request)
    #
    #     if user.is_authenticated():
    #         return user
    #     else:
    #         if not self.request.headers.has_key('Authorization'):
    #             return None
    #
    #         kind, data = self.request.headers['Authorization'].split(' ')
    #         if kind != 'Basic':
    #             return None
    #
    #         (username, _, password) = data.decode('base64').partition(':')
    #         user = authenticate(username=username, password=password)
    #         if user is not None and user.is_authenticated():
    #             return user
    #
    #     return None
    #
    # def get_django_session(self):
    #     if not hasattr(self, '_session'):
    #         session_key = self.get_cookie(settings)
    #         session_engine = import_module(settings.SESSION_ENGINE)
    #         self._session = session_engine.SessionStore(session_key)
    #         return self._session
    #     return None
    #
    # def get_django_request(self):
    #     request = WSGIRequest(WSGIContainer.environ(self.request))
    #     request.session = self.get_django_session()
    #
    #     if self.current_user:
    #         request.user = self.current_user
    #     else:
    #         request.user = AnonymousUser()
    #
    #     return request


def main():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'project_dj.settings'

    # print 'django version: {0}, {1}'.format(django.VERSION, django.VERSION[1])
    if django.VERSION[1] > 5:
        django.setup()

    parse_command_line()

    wsgi_app = get_wsgi_application()
    wsgi_container = WSGIContainer(wsgi_app)
    # wsgi_container = WSGIContainer(WSGIHandler)
    tornado_app = Application([
        ('/ws', WSHandler),
        ('/hello-tornado', HelloTornado),
        ('.*', FallbackHandler, dict(fallback=wsgi_container)),
    ])

    http_server = HTTPServer(tornado_app)
    http_server.listen(options.port, address=options.host)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()