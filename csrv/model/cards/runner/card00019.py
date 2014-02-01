from csrv.model.cards import card_info
from csrv.model.cards import event


class Card00019(event.Event):

  NAME = u'Card00019'
  SET = card_info.CORE
  NUMBER = 19
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.JOB,
  ])
  COST = 0
  IMAGE_SRC = '01019.png'

  def build_actions(self):
    event.Event.build_actions(self)

  def play(self):
    self.game.runner.credits.gain(3)
