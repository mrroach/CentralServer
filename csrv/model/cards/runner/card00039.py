from csrv.model.cards import card_info
from csrv.model.cards import hardware


class Card00039(hardware.Hardware):

  NAME = u'Card00039'
  SET = card_info.CORE
  NUMBER = 39
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.LINK,
  ])
  COST = 2
  IMAGE_SRC = '01039.png'

  def build_actions(self):
    hardware.Hardware.build_actions(self)
