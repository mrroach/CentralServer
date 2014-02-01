"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class InstallUpgrade(action.Action):

  DESCRIPTION = '[click]: Install an agenda, asset, upgrade, or piece of ice'
  COST_CLASS = cost.InstallAgendaAssetUpgradeCost
  REQUEST_CLASS = parameters.InstallUpgradeRequest

  def __init__(self, game, player, card=None, cost=None, server=None):
    action.Action.__init__(self, game, player, card=card, cost=cost)
    self.server = server

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if self.server:
      if not response or not response.server == self.server:
        raise errors.InvalidResponse(
            'Can only be installed in %s' % self.server)
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    if response and response.server:
      server = response.server
      for card in response.cards_to_trash:
        # This gets repeated a lot. move to player
        server.uninstall(card)
        self.player.archives.add(card)
    else:
      server = self.player.new_remote_server()
    self.card.install(server)

  @property
  def description(self):
    return 'Install %s' % self.card.NAME
