from pprint import pprint
import json
import pickle
import traceback
import tornado.web
from tornado import websocket
from csrv.model import json_serializer
from csrv.server import data


class ViewHandler(tornado.web.RequestHandler):
  def get(self, game_id, side):
    game_data = data.Data.get(game_id)
    assert(game_data)
    assert(game_data.game)
    if side == 'corp':
      self.render('corp_view.html',
                  game_id=game_id, side=side, xsrf_token=self.xsrf_token)
    else:
      self.render('runner_view.html',
                  game_id=game_id, side=side, xsrf_token=self.xsrf_token)


class GameStateHandler(tornado.web.RequestHandler):
  def get(self, game_id, side):
    game_data = data.Data.get(game_id)
    if side == 'corp':
      json = json_serializer.serialize_game_corp(game_data.game)
      self.set_header('Content-Type', 'application/json')
      self.write(json)
    else:
      json = json_serializer.serialize_game_runner(game_data.game)
      self.set_header('Content-Type', 'application/json')
      self.write(json)


class ChoicesHandler(tornado.web.RequestHandler):
  """Serialize and deserialize game choices."""

  def get(self, game_id, side):
    game_data = data.Data.get(game_id)
    assert(game_data)
    assert(game_data.game)
    phase = game_data.game.current_phase()
    if side == str(phase.player):
      json_data = json_serializer.serialize_choices(game_data.game)
    else:
      json_data = json_serializer.serialize_choices(
          game_data.game, secret=True)
    self.set_header('Content-Type', 'application/json')
    self.write(json_data)

  def post(self, game_id, side):
    game_data = data.Data.get(game_id)
    assert(game_data)
    assert(game_data.game)
    choice_data = json.loads(self.request.body)
    phase = game_data.game.current_phase()
    if side == str(phase.player):
      index = choice_data['index']
      if index is None:
        choice = None
        response = None
      else:
        choice = phase.choices()[index]
        response = json_serializer.deserialize_response(
            game_data.game, choice_data['response'])
      game_data.game.resolve_current_phase(choice, response)
      data.Data.dump(game_id)
    return self.get(game_id, side)


class PickleHandler(tornado.web.RequestHandler):
  """Return a pickled game object."""

  def get(self, game_id):
    game_data = data.Data.get(game_id)
    self.set_header('Content-Type', 'application/octet-stream')
    self.set_header('Content-Disposition', 'inline; filename="game.p"')
    self.write(pickle.dumps(game_data.game))


class GameSocketHandler(websocket.WebSocketHandler):
  def open(self, game_id, side):
    self.side = side
    self.game_id = game_id
    self.game_data = data.Data.get(game_id)
    for handler in self.game_data.handlers:
      if handler.side == self.side:
        print 'someone else is already logged in as %s' % side
        self.close()
        return
    self.game_data.handlers.append(self)
    self.log_position = 0
    self.send_game_state()

  def on_message(self, message):
    print message
    choice_data = json.loads(message)
    phase = self.game_data.game.current_phase()
    if choice_data['choiceCount'] != self.game_data.game.choice_count:
      print "Got choice data for wrong choice."
      return
    if self.side == str(phase.player):
      print 'Received choice for %s %s:%s' % (
          self.game_data.game.choice_count, self.side, phase)
      index = choice_data['index']
      if index is None:
        choice = None
        response = None
      else:
        if len(phase.choices()) > index:
          choice = phase.choices()[index]
          response = json_serializer.deserialize_response(
              self.game_data.game, choice_data['response'])
        else:
          return self.send_error('Got index %s for %s' % (index,
            phase.choices()))
      try:
        self.game_data.game.resolve_current_phase(choice, response)
        data.Data.dump(self.game_id)
      except Exception as e:
        return self.send_error(traceback.format_exc())
    else:
      return self.send_error('Got choice on other player turn.: %s' %
          message)
    self.send_game_state()
    for handler in self.game_data.handlers:
      if not handler is self:
        handler.send_game_state()

  def send_game_state(self):
    if self.game_data.game.run:
      pprint(self.game_data.game.run._phases)
    if self.side == str(self.game_data.game.current_phase().player):
      print 'Sending data for %s %s:%s (%s choices)' % (
          self.game_data.game.choice_count, self.side,
          self.game_data.game.current_phase(),
          len(self.game_data.game.current_phase().choices()))

    if self.side == 'corp':
      json_data = json_serializer.serialize_game_corp(self.game_data.game)
    else:
      json_data = json_serializer.serialize_game_runner(self.game_data.game)
    self.write_message(json_data)

    if self.log_position < len(self.game_data.game._log):
      log_data = {'log': []}
      for log in self.game_data.game._log[self.log_position:]:
        log_data['log'].append(log)
      self.log_position = len(self.game_data.game._log)
      self.write_message(json.dumps(log_data))

  def send_error(self, message):
    message = json.dumps({'error': message})
    self.write_message(message)

  def on_close(self):
    self.game_data.handlers.remove(self)
