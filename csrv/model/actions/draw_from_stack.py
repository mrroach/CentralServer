"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class DrawFromStack(action.Action):

  DESCRIPTION = '[click]: Draw one card from your stack'
  COST_CLASS = cost.BasicActionCost

  def is_usable(self):
    return bool(self.cost.can_pay() and self.player.stack.cards)

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    card = self.player.stack.pop()
    self.player.grip.add(card)
    self.player.stack.log('The runner draws a card from the stack')
    self.trigger_event(events.DrawFromStack(self.game, self.player))


