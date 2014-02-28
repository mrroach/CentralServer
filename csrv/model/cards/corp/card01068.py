from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import agenda
from csrv.model.cards import card_info


class EndTheRun(actions.Action):
  DESCRIPTION = 'End the run using agenda counter from Card01068'

  def resolve(self, response=None):
    self.card.agenda_counters -= 1
    self.game.run.end()


class Card01068(agenda.Agenda):

  NAME = u'Card01068'
  SET = card_info.CORE
  NUMBER = 68
  SIDE = card_info.CORP
  FACTION = card_info.NETCORP
  UNIQUE = False
  KEYWORDS = set([
      card_info.INITIATIVE,
  ])
  ADVANCEMENT_REQUIREMENT = 4
  AGENDA_POINTS = 2
  IMAGE_SRC = '01068.png'

  WHEN_IN_CORP_SCORE_AREA_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpUseAbilities: 'end_the_run_abilities',
  }

  def build_actions(self):
    agenda.Agenda.build_actions(self)

  def end_the_run_abilities(self):
    if self.agenda_counters and self.game.run:
      return [EndTheRun(self.game, self.player, card=self)]
    else:
      return []

  def score(self):
    agenda.Agenda.score(self)
    self.agenda_counters += 1
