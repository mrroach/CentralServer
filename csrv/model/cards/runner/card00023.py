from csrv.model.cards import card_info
from csrv.model.cards import hardware


class Card00023(hardware.Hardware):

  NAME = u'Card00023'
  SET = card_info.CORE
  NUMBER = 23
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 1
  UNIQUE = False
  COST = 1
  IMAGE_SRC = '01023.png'

  def build_actions(self):
    hardware.Hardware.build_actions(self)
