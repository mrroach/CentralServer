"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters
from csrv.model.cards import card_info


class InstallAgendaAsset(action.Action):

  DESCRIPTION = '[click]: Install an agenda, asset, upgrade, or piece of ice'
  COST_CLASS = cost.InstallAgendaAssetUpgradeCost
  REQUEST_CLASS = parameters.InstallAgendaAssetRequest

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    to_trash = []
    if response and response.server:
      server = response.server
      if server in [self.player.hq, self.player.archives, self.player.rnd]:
        raise errors.InvalidResponse(
            'Assets and agendas cannot be installed in central servers')
      to_trash = response.cards_to_trash + [
          c for c in server.installed.cards
          if c.TYPE in [card_info.AGENDA, card_info.ASSET]]
    else:
      server = self.player.new_remote_server()
    # do the install before removing so that the remote doesn't cease to exist
    self.card.install(server)
    for card in to_trash:
      card.trash()

  @property
  def description(self):
    return 'Install %s' % self.card.NAME
