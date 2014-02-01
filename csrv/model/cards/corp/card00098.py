from csrv.model.cards import card_info
from csrv.model.cards import operation


class Card00098(operation.Operation):

  NAME = u'Card00098'
  SET = card_info.CORE
  NUMBER = 98
  SIDE = card_info.CORP
  FACTION = card_info.MEATCORP
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.TRANSACTION,
  ])
  COST = 0
  IMAGE_SRC = '01098.png'

  def build_actions(self):
    operation.Operation.build_actions(self)

  def play(self):
    operation.Operation.play(self)
    self.player.credits.gain(3)
