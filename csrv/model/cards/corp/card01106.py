from csrv.model import actions
from csrv.model import cost
from csrv.model import timing_phases
from csrv.model.cards import agenda
from csrv.model.cards import card_info


class RezIce(actions.RezIce):
  COST_CLASS = cost.NullCost


class RezIcePhase(timing_phases.BasePhase):
  """Rez a piece of ice ignoring all costs."""

  NULL_OK = True
  NULL_CHOICE = 'Do not rez any ice'

  def choices(self, refresh=False):
    actions = []
    for server in self.game.corp.servers:
      for ice in server.ice.cards:
        if not ice.is_rezzed:
          actions.append(
              RezIce(self.game, self.player, ice))
    return actions

  def resolve(self, choice, response=None):
    timing_phases.BasePhase.resolve(self, choice, response=response)
    if choice:
      self.end_phase()


class Card01106(agenda.Agenda):

  NAME = u'Card01106'
  SET = card_info.CORE
  NUMBER = 106
  SIDE = card_info.CORP
  FACTION = card_info.NEUTRAL
  INFLUENCE = 0
  UNIQUE = False
  KEYWORDS = set([
      card_info.SECURITY,
  ])
  ADVANCEMENT_REQUIREMENT = 5
  AGENDA_POINTS = 3
  IMAGE_SRC = '01106.png'

  def build_actions(self):
    agenda.Agenda.build_actions(self)

  def score(self):
    agenda.Agenda.score(self)
    self.game.insert_next_phase(RezIcePhase(self.game, self.player))
