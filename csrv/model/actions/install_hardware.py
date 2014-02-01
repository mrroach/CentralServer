"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class InstallHardware(action.Action):

  DESCRIPTION = '[click]: Install a piece of hardware'
  COST_CLASS = cost.InstallHardwareCost
  REQUEST_CLASS = parameters.InstallHardwareRequest

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if (not ignore_all_costs and
        not self.cost.can_pay(response, ignore_clicks=ignore_clicks)):
      raise errors.CostNotSatisfied(
          'Not enough credits to install in that location.')
    if response and response.host:
      if not response.host in self.card.install_host_targets():
        raise errors.InvalidResponse(
            'Cannot host this type of card')
      response.host.host_card(self.card)
    action.Action.resolve(self, response,
                          ignore_clicks=ignore_clicks,
                          ignore_all_costs=ignore_all_costs)
    self.card.log('The runner installs %s' % self.card)

    self.player.rig.add(self.card)

  @property
  def description(self):
    return 'Install %s' % self.card.NAME


