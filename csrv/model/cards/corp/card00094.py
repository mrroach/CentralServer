from csrv.model.cards import agenda
from csrv.model.cards import card_info


class Card00094(agenda.Agenda):

  NAME = u'Card00094'
  SET = card_info.CORE
  NUMBER = 94
  SIDE = card_info.CORP
  FACTION = card_info.MEATCORP
  UNIQUE = False
  KEYWORDS = set([
      card_info.EXPANSION,
  ])
  ADVANCEMENT_REQUIREMENT = 2
  AGENDA_POINTS = 1
  IMAGE_SRC = '01094.png'

  def build_actions(self):
    agenda.Agenda.build_actions(self)

  def score(self):
    agenda.Agenda.score(self)
    self.game.corp.credits.gain(7)
    self.game.corp.bad_publicity += 1
