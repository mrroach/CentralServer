from csrv.model.cards import card_info
from csrv.model.cards import event


class Card01050(event.Event):

  NAME = u'Card01050'
  SET = card_info.CORE
  NUMBER = 50
  SIDE = card_info.RUNNER
  FACTION = card_info.NEUTRAL
  INFLUENCE = 0
  UNIQUE = False
  COST = 5
  IMAGE_SRC = '01050.png'

  def build_actions(self):
    event.Event.build_actions(self)

  def play(self):
    self.game.runner.credits.gain(9)
