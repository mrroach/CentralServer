"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class GainACredit(action.Action):

  DESCRIPTION = '[click]: Gain 1[cred] (one credit)'
  COST_CLASS = cost.BasicActionCost

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.player.credits.gain(1)
    self.game.log('The %s gains 1[cred]' % self.player, None)
    self.trigger_event(events.GainACredit(self.game, self.player))
