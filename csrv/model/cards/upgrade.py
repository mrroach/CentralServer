"""An upgrade card."""

from csrv.model import actions
from csrv.model import events
from csrv.model import game_object
from csrv.model import timing_phases
from csrv.model.cards import installable_card


class Upgrade(installable_card.InstallableCard):

  TYPE = 'Upgrade'
  REZZABLE = True

  WHEN_IN_HAND_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpTurnActions: 'install_actions',
  }

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR ={
      timing_phases.CorpRezCards: 'rez_actions',
  }

  WHEN_ACCESSED_PROVIDES_CHOICES_FOR = {
    timing_phases.AccessCard: 'trash_on_access_actions',
  }

  def build_actions(self):
    installable_card.InstallableCard.build_actions(self)
    self.install_action = actions.InstallUpgrade(
        self.game, self.player, self)
    self._rez_action = actions.RezAssetUpgrade(self.game, self.player, self)

  def install_actions(self):
    return [self.install_action]

  def rez_actions(self):
    if not self.is_rezzed:
      return [self._rez_action]
    return []

  def on_install(self):
    installable_card.InstallableCard.on_install(self)
    self.trigger_event(events.InstallAgendaAssetUpgrade(self.game, self.player))
