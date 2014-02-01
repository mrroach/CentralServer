#!/usr/bin/env python
import os
import tornado.ioloop
import tornado.web
from tornado import options
from csrv.server import new_game
from csrv.server import deck_handler
from csrv.server import wait_handler
from csrv.server import view_handler

options.define('port', default=8080, help='Run on the given port.')


class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.render('index.html')


def main():
  options.parse_command_line()
  application = tornado.web.Application(
      [
          ('/', MainHandler),
          (r'/game/new', new_game.NewGameHandler),
          (r'/game/load', new_game.LoadGameHandler),
          (r'/game/(\d+)/(corp|runner)/deck', deck_handler.DeckHandler),
          (r'/game/(\d+)/(corp|runner)/wait', wait_handler.WaitHandler),
          (r'/game/(\d+)/(corp|runner)/view', view_handler.ViewHandler),
          (r'/game/(\d+)/(corp|runner)/game_state.json',
            view_handler.GameStateHandler),
          (r'/game/(\d+)/(corp|runner)/choices.json',
            view_handler.ChoicesHandler),
          (r'/game/(\d+)/(corp|runner)/sock',
            view_handler.GameSocketHandler),
          (r'/game/(\d+)', view_handler.PickleHandler),
      ],
      template_path=os.path.join(os.path.dirname(__file__), 'templates'),
      static_path=os.path.join(os.path.dirname(__file__), 'static'),
      xsrf_cookies=True,
      debug=True,
  )
  application.listen(options.options.port)
  tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
  main()
