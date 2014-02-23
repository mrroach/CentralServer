"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class RezIce(action.Action):

  COST_CLASS = cost.RezIceCost
  DESCRIPTION = 'Rez a piece of ice.'

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        response=response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.card.log('The corp rezzes %s' % self.card)
    self.card.rez()

  @property
  def description(self):
    return 'Rez %s' % self.card
