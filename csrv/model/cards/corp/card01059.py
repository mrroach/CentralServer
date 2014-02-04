from csrv.model.cards import card_info
from csrv.model.cards import operation


class Card01059(operation.Operation):

  NAME = u'Card01059'
  SET = card_info.CORE
  NUMBER = 59
  SIDE = card_info.CORP
  FACTION = card_info.ROBOCORP
  INFLUENCE = 4
  UNIQUE = False
  COST = 4
  IMAGE_SRC = '01059.png'

  def build_actions(self):
    operation.Operation.build_actions(self)

  def play(self):
    self.player.clicks.gain(2)
