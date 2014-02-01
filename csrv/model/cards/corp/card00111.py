from csrv.model.actions import subroutines
from csrv.model.cards import card_info
from csrv.model.cards import ice


class Card00111(ice.Ice):

  NAME = u'Card00111'
  SET = card_info.CORE
  NUMBER = 111
  SIDE = card_info.CORP
  FACTION = card_info.NEUTRAL
  INFLUENCE = 0
  UNIQUE = False
  KEYWORDS = set([
      card_info.CODE_GATE,
  ])
  COST = 3
  IMAGE_SRC = '01111.png'
  STRENGTH = 2

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        subroutines.LoseClickIfAble(game, player),
        subroutines.EndTheRun(game, player),
    ]

  def build_actions(self):
    ice.Ice.build_actions(self)
