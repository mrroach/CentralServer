"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class CardClickAbility(action.Action):

  DESCRIPTION = 'Trigger a [click] ability on an active card.'

  def __init__(self, game, player, card, ability, method, cost=None):
    action.Action.__init__(self, game, player, card=card, cost=cost)
    self.ability = ability
    self.method = method

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    # The card must handle click/credit accounting
    self.card.log("The %s uses %s's '%s' ability" %
                  (self.player, self.card.NAME, self.ability))
    getattr(self.card, self.method)()

  @property
  def description(self):
    return "Use %s's '%s' ability" % (self.card.NAME, self.ability)


