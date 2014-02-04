from csrv.model.cards import card_info
from csrv.model.cards import operation


class Card01100(operation.Operation):

  NAME = u'Card01100'
  SET = card_info.CORE
  NUMBER = 100
  SIDE = card_info.CORP
  FACTION = card_info.MEATCORP
  INFLUENCE = 1
  UNIQUE = False
  COST = 0
  IMAGE_SRC = '01100.png'

  def build_actions(self):
    operation.Operation.build_actions(self)
