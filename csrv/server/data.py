import threading
import cPickle

class GameData(object):
  def __init__(self):
    self.runner_deck = None
    self.corp_deck = None
    self.game = None
    self.handlers = []


class Data(object):
  """A really dumb in-memory store"""

  GAMES = {}
  GAME_IDX = 0
  GAME_LOCK = threading.Lock()

  @classmethod
  def new_game(cls):
    with cls.GAME_LOCK:
      cls.GAME_IDX += 1
      game_data = GameData()
      # Use strings for index so controllers don't have to cast
      cls.GAMES[str(cls.GAME_IDX)] = game_data
    return str(cls.GAME_IDX)

  @classmethod
  def get(cls, idx):
    return cls.GAMES.get(idx)

  @classmethod
  def dump(cls, idx):
    ""
