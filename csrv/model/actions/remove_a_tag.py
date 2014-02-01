"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import appropriations
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class RemoveATag(action.Action):

  DESCRIPTION = '[click], 2 [Credits]: Remove 1 tag'

  def __init__(self, game, player):
    cost_obj = cost.Cost(game, player, clicks=1, credits=2,
                         appropriations=[appropriations.REMOVE_TAGS])
    action.Action.__init__(self, game, player, cost=cost_obj)

  def is_usable(self):
    return bool(self.cost.can_pay() and self.player.tags)

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.player.tags -= 1
    self.player.stack.log('The runner removes 1 tag')
