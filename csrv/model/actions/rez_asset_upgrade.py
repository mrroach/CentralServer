"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class RezAssetUpgrade(action.Action):

  COST_CLASS = cost.RezAssetUpgradeCost
  DESCRIPTION = 'Rez an asset or upgrade'

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.card.rez()
    self.trigger_event(events.RezAssetUpgrade(self.game, self.player))

  @property
  def description(self):
    return 'Rez %s' % self.card.NAME

