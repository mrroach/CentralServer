from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.actions import subroutines
from csrv.model.cards import card_info
from csrv.model.cards import ice


class Card01113(ice.Ice):

  NAME = 'Card01113'
  STRENGTH = 3
  COST = 3
  FACTION = card_info.NEUTRAL
  KEYWORDS = set([
      card_info.BARRIER,
  ])
  INFLUENCE = 0
  NUMBER = 113
  SET = card_info.CORE
  IMAGE_SRC = '01113.png'

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        subroutines.EndTheRun(self.game, self.player)
    ]
