"""Base actions for the players to take."""

from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters
from csrv.model.actions import action


class AdvanceCard(action.Action):

  DESCRIPTION = '[click], [cred]: Advance a card'
  COST_CLASS = cost.AdvanceCardCost

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.card.advance()

  @property
  def description(self):
    return 'Advance %s' % self.card.NAME


