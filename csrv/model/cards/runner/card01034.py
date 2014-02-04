from csrv.model.cards import card_info
from csrv.model.cards import event


class Card01034(event.Event):

  NAME = u'Card01034'
  SET = card_info.CORE
  NUMBER = 34
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 2
  UNIQUE = False
  COST = 0
  IMAGE_SRC = '01034.png'

  def build_actions(self):
    event.Event.build_actions(self)

  def play(self):
    for i in range(3):
      card = self.player.stack.pop()
      self.player.grip.add(card)
