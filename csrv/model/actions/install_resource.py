"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class InstallResource(action.Action):

  DESCRIPTION = '[click]: Install a resource'
  COST_CLASS = cost.InstallResourceCost
  REQUEST_CLASS = parameters.InstallResourceRequest

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if (not ignore_all_costs and
        not self.cost.can_pay(response)):
      raise errors.CostNotSatisfied(
          'Not enough credits to install in that location.')
    action.Action.resolve(self, response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=False)
    self.player.rig.add(self.card)

  @property
  def description(self):
    return 'Install %s' % self.card.NAME
