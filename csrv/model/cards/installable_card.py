"""Basic implementation of a card."""

from csrv.model import actions
from csrv.model.cards import card_base
from csrv.model import game_object
from csrv.model import timing_phases


class InstallableCard(card_base.CardBase):

  def build_actions(self):
    card_base.CardBase.build_actions(self)
    self._trash_on_access = None

  def _trash_on_access_action(self):
    if not self._trash_on_access:
      self._trash_on_access = actions.TrashOnAccess(
        self.game, self.game.runner, self)
    return self._trash_on_access

  def trash_on_access_actions(self):
    if not self.location == self.game.corp.archives:
      return [self._trash_on_access_action()]
    return []

  def abilities(self):
    return []

  def install(self, server):
    self.location.remove(self)
    self.is_installed = True
    self.player.installed_cards.add(self)
    server.install(self)
