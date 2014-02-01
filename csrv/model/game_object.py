from csrv.model import callback_manager


class GameObject(object):
  """Base class for game elements which emit/respond to events."""

  LISTENS = []
  PREVENTS = []
  PROVIDES_CHOICES_FOR = {}

  def __init__(self, game):
    self.game = game
    for event in self.LISTENS:
      self.game.register_listener(event, self)
    for timing_phase, method in self.PROVIDES_CHOICES_FOR.iteritems():
      self.game.register_choice_provider(timing_phase, self, method)
    self.game_id = None

  def set_new_id(self):
    old_id = self.game_id
    self.game_id = self.game.new_id()
    self.game.register_game_object(self, old_id)

  def trigger_event(self, event):
    """Send a game event to all listeners.

    The class object will be used as the signal, and the instance
    will contain any needed data.
    """
    self.game.trigger_event(event, self)

  def log(self, message):
    """Log a message with the current game id.

    game id is used instead of a reference to self to avoid leaking info.

    Args:
      message: str, The message to log. Should be free of any secret info.
    """
    self.game.log(message, self.game_id)


class PlayerObject(GameObject):
  """Game elements which are associated with a particular player."""

  def __init__(self, game, player):
    GameObject.__init__(self, game)
    self.player = player
