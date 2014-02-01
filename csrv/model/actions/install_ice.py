"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class InstallIce(action.Action):

  DESCRIPTION = '[click]: Install an agenda, asset, upgrade, or piece of ice'
  COST_CLASS = cost.InstallIceCost
  REQUEST_CLASS = parameters.InstallIceRequest

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if (not ignore_all_costs and
        not self.cost.can_pay(response, ignore_clicks=ignore_clicks)):
      raise errors.CostNotSatisfied(
          'Not enough credits to install in that location.')
    action.Action.resolve(self, response,
                          ignore_clicks=ignore_clicks,
                          ignore_all_costs=ignore_all_costs)
    if response and response.server:
      server = response.server
    else:
      server = self.player.new_remote_server()
    self.card.log('The corp installs ice protecting %s' % server)
    server.install_ice(self.card)

  @property
  def description(self):
    return 'Install %s' % self.card.NAME
