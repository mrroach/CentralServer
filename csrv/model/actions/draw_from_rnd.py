"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class DrawFromRnD(action.Action):

  DESCRIPTION = '[click]: Draw one card from R&D'
  COST_CLASS = cost.BasicActionCost

  def is_usable(self):
    return bool(self.cost.can_pay() and self.player.rnd.cards)

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    card = self.player.rnd.pop()
    self.player.hq.add(card)
    self.player.rnd.log('The corp draws a card from R&D')
    self.trigger_event(events.DrawFromRnD(self.game, self.player))


