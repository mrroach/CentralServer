from csrv.model.cards import card_info
from csrv.model.cards import operation


class Card00110(operation.Operation):

  NAME = 'Card00110'
  SUBTYPES = ['Transaction']
  COST = 5
  FACTION = 'Neutral'
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

