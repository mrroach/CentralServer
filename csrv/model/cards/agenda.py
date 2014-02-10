"""Basic implementation of a card."""

from csrv.model import actions
from csrv.model import events
from csrv.model import game_object
from csrv.model import modifiers
from csrv.model import timing_phases
from csrv.model.cards import installable_card
from csrv.model.cards import card_info


class Agenda(installable_card.InstallableCard):

  TYPE = card_info.AGENDA
  ADVANCEABLE = True
  TRASHABLE = False

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpTurnActions: 'installed_actions',
      timing_phases.CorpScoreAgendas: 'score_actions',
  }

  WHEN_IN_HAND_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpTurnActions: 'in_hand_actions',
  }

  WHEN_ACCESSED_PROVIDES_CHOICES_FOR = {
    timing_phases.AccessCard: 'steal_agenda_actions',
  }

  @property
  @modifiers.modifiable(modifiers.AgendaAdvancementRequirement)
  def advancement_requirement(self):
    return self.ADVANCEMENT_REQUIREMENT

  @property
  def agenda_points(self):
    return self.AGENDA_POINTS

  def can_score(self):
    return self.advancement_tokens >= self.advancement_requirement

  def build_actions(self):
    installable_card.InstallableCard.build_actions(self)
    self.install_action = actions.InstallAgendaAsset(
        self.game, self.player, self)
    self._advance_action = actions.AdvanceCard(self.game, self.player, self)
    self._score_action = actions.ScoreAgenda(self.game, self.player, self)
    self._steal_action = actions.StealAgenda(self.game, self.game.runner, self)

  @property
  @modifiers.modifiable(modifiers.StealAgendaCost)
  def steal_cost(self):
    return 0

  def installed_actions(self):
    return [self._advance_action]

  def score_actions(self):
    if self.can_score():
      return [self._score_action]
    return []

  def steal_agenda_actions(self):
    return [self._steal_action]

  def in_hand_actions(self):
    return [self.install_action]

  def score(self):
    self.location.parent.uninstall(self)
    self.player.scored_agendas.add(self)
    self.player.agenda_points += self.agenda_points
    self.on_score()

  def on_score(self):
    pass

  def on_install(self):
    installable_card.InstallableCard.on_install(self)
    self.trigger_event(events.InstallAgendaAssetUpgrade(self.game, self.player))
