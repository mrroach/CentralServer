"""A resource card."""

from csrv.model import actions
from csrv.model.cards import card_base
from csrv.model import game_object
from csrv.model import timing_phases
from csrv.model.cards import card_info


class Resource(card_base.CardBase):

  TYPE = card_info.RESOURCE

  WHEN_IN_HAND_PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnActions: 'install_actions',
  }

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpTurnActions: 'trash_if_tagged_actions',
  }

  def build_actions(self):
    card_base.CardBase.build_actions(self)
    self.install_action = actions.InstallResource(
        self.game, self.player, self)

  def install_actions(self):
    if self.player.clicks.value:
      return [self.install_action]
    return []

  def trash_if_tagged_actions(self):
    if self.game.runner.tags:
      return [actions.TrashResource(self.game, self.game.corp, self)]
    return []

