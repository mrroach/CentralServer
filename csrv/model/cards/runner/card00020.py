from csrv.model.cards import card_info
from csrv.model.cards import event


class Card00020(event.Event):

  NAME = u'Card00020'
  SET = card_info.CORE
  NUMBER = 20
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.SABOTAGE,
  ])
  COST = 1
  IMAGE_SRC = '01020.png'

  def build_actions(self):
    event.Event.build_actions(self)
