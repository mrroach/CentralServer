"""Base actions for the players to take."""

from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class Action(game_object.PlayerObject):
  COST_CLASS = cost.NullCost
  REQUEST_CLASS = parameters.NullRequest
  DESCRIPTION = 'Oops. This action has no description!'

  def __init__(self, game, player, card=None, cost=None):
    game_object.PlayerObject.__init__(self, game, player)
    self.card = card
    self._is_mandatory = False
    if cost:
      self.cost = cost
    else:
      self.cost = self.COST_CLASS(game, player, card=card)

  def is_usable(self):
    return self.cost.can_pay()

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if not ignore_all_costs:
      self.cost.pay(response, ignore_clicks=ignore_clicks)

  @property
  def is_mandatory(self):
    return self._is_mandatory

  @property
  def description(self):
    return self.DESCRIPTION

  def __str__(self):
    return self.description

  def request(self):
    return self.REQUEST_CLASS(self.game, self.card)


