from csrv.model.cards import card_info
from csrv.model.cards import operation


class Card00073(operation.Operation):

  NAME = u'Card00073'
  SET = card_info.CORE
  NUMBER = 73
  SIDE = card_info.CORP
  FACTION = card_info.NETCORP
  INFLUENCE = 3
  UNIQUE = False
  COST = 0
  IMAGE_SRC = '01073.png'

  def build_actions(self):
    operation.Operation.build_actions(self)
