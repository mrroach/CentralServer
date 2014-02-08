from csrv.model.cards import card_info
from csrv.model.cards import operation


class Card01110(operation.Operation):

  NAME = 'Card01110'
  SUBTYPES = [card_info.TRANSACTION]
  COST = 5
  FACTION = card_info.NEUTRAL
  INFLUENCE = 0
  NUMBER = 110
  SET = card_info.CORE
  IMAGE_SRC = '01110.png'
  KEYWORDS = [
      card_info.TRANSACTION
  ]

  def play(self):
    operation.Operation.play(self)
    self.player.credits.gain(9)

