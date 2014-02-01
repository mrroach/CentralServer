import pickle
import tornado.web
from csrv.model import deck
from csrv.model.cards import corp
from csrv.model.cards import runner
from csrv.model import json_serializer
from csrv.model import game
from csrv.server import data


class NewGameHandler(tornado.web.RequestHandler):
  def get(self):
    self.render('new_game.html', errors=[])

  def post(self):
    side = self.get_argument('side', '')
    if side not in ['runner', 'corp']:
      self.render('new_game.html',
                  errors=['You must pick either runner or corp'])
    else:
      game_id = data.Data.new_game()
      self.redirect('/game/%s/%s/deck' % (game_id, side))

  def get_template_namesspace(self):
    default = tornado.web.RequestHandler.get_template_namespace(self)
    default['errors'] = []
    return default

class LoadGameHandler(tornado.web.RequestHandler):
  def get(self):
    self.render('load_game.html')

  def post(self):
    side = self.get_argument('side')
    game_id = data.Data.new_game()
    game_obj = pickle.loads(self.request.files.get('pickle')[0]['body'])
    game_data = data.Data.get(game_id)
    game_data.game = game_obj
    self.redirect('/game/%s/%s/view' % (game_id, side))
