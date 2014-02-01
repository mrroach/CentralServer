from csrv.model.cards import card_info
from csrv.model.cards import ice
from csrv.model.actions import subroutines
from csrv.model.actions.subroutines import trash_a_program


class Card00064(ice.Ice):

  NAME = u'Card00064'
  SET = card_info.CORE
  NUMBER = 64
  SIDE = card_info.CORP
  FACTION = card_info.ROBOCORP
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.DESTROYER,
      card_info.SENTRY,
  ])
  COST = 4
  IMAGE_SRC = '01064.png'
  STRENGTH = 0

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        trash_a_program.TrashAProgram(self.game, self.player),
        subroutines.EndTheRun(self.game, self.player),
    ]

  def build_actions(self):
    ice.Ice.build_actions(self)
