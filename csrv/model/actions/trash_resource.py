"""Trash a resource when the runner is tagged."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors


class TrashResource(action.Action):

  DESCRIPTION = 'Trash a resource'

  def __init__(self, game, player, card):
    cost_obj = cost.Cost(game, player, card=card, clicks=1, credits=2)
    action.Action.__init__(self, game, player, card, cost=cost_obj)

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.card.log('The corp trashes %s' % self.card.NAME)
    self.card.trash()

  @property
  def description(self):
    return 'Trash %s' % self.card.NAME
