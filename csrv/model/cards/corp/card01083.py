from csrv.model.cards import card_info
from csrv.model.cards import operation


class Card01083(operation.Operation):

  NAME = u'Card01083'
  SET = card_info.CORE
  NUMBER = 83
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  INFLUENCE = 1
  UNIQUE = False
  COST = 0
  IMAGE_SRC = '01083.png'

  def build_actions(self):
    operation.Operation.build_actions(self)

  def play(self):
    for _ in range(3):
      card = self.player.rnd.pop()
      self.player.hq.add(card)
