import tornado.web
from csrv.server import data


class WaitHandler(tornado.web.RequestHandler):
  def get(self, game_id, side):
    game_data = data.Data.get(game_id)
    assert(game_data)
    if game_data.game:
      self.redirect('/game/%s/%s/view' % (game_id, side))
    else:
      self.render('wait.html', game_id=game_id, side=side)

