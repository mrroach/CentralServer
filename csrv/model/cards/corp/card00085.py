from csrv.model.cards import card_info
from csrv.model.cards import operation


class Card00085(operation.Operation):

  NAME = u'Card00085'
  SET = card_info.CORE
  NUMBER = 85
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  INFLUENCE = 3
  UNIQUE = False
  COST = 0
  IMAGE_SRC = '01085.png'

  def build_actions(self):
    operation.Operation.build_actions(self)
