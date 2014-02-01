from csrv.model import errors
from csrv.model import events
from csrv.model import game_object


class Pool(game_object.PlayerObject):
  """A pool of static or recurring values (credits/clicks)."""

  def __init__(self, game, player, starting_value=0):
    game_object.PlayerObject.__init__(self, game, player)
    self.value = starting_value
    self.starting_value = starting_value

  def reset(self):
    self.value = self.starting_value

  def set(self, value):
    self.value = value

  def gain(self, num):
    self.value += num

  def lose(self, num):
    if (self.value - num) < 0:
      raise errors.InsufficientFunds(
          'You (%s) cannot afford %d' % (self.player, num))
    self.value -= num
  spend = lose


class RecurringPool(Pool):
  """A pool which resets at the beginning of each turn."""

  LISTENS = [
    events.CorpTurnBegin,
    events.RunnerTurnBegin,
  ]

  def on_turn_begin(self, sender, event):
    self.reset()

  on_corp_turn_begin = on_turn_begin
  on_runner_turn_begin = on_turn_begin


class CreditPool(Pool):
  """A pool of money. Potentially spendable only on certain actions."""

  def __init__(self, game, player, starting_value=0,
      appropriation=None, recurring=False):
    Pool.__init__(self, game, player, starting_value)
    # specific abilities the money may be spent on
    self.appropriation = appropriation if appropriation is not None else set()
    self.recurring = recurring
    if recurring:
      self.game.register_listener(events.CorpTurnBegin, self)
      self.game.register_listener(events.RunnerTurnBegin, self)

  def on_turn_begin(self, sender, event):
    self.reset()

  on_corp_turn_begin = on_turn_begin
  on_runner_turn_begin = on_turn_begin

  def remove(self):
    if self.recurring:
      self.game.deregister_listener(events.CorpTurnBegin, self)
      self.game.deregister_listener(events.RunnerTurnBegin, self)

  def utility(self):
    """Return a numeric proxy for the number of ways the pool can be used."""
    return len(self.appropriation)


class MainCreditPool(CreditPool):
  """The main credit pool for a player. Spendable on anything."""

  def utility(self):
    """Use these credits last."""
    return 999


class EphemeralCreditPool(CreditPool):
  """Real credits. Spendable on anything. Disappears after a while."""

  def utility(self):
    """This is a tough one.

    Use almost last to avoid screwing self over right now. This may not always
    be optimal for longer term benefit."""
    return 998


class ClickPool(Pool):
  """A pool which resets during the action phase."""

  LISTENS = [
    events.CorpActionPhase,
    events.RunnerActionPhase,
  ]

  def on_action_phase(self, sender, event):
    if sender.player == self.player:
      self.reset()
  on_corp_action_phase = on_action_phase
  on_runner_action_phase = on_action_phase

