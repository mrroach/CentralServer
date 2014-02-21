from csrv.model.cards import card_info
from csrv.model.cards import ice
from csrv.model.actions import subroutines
from csrv.model.actions.subroutines import do_net_damage


class Card01078(ice.Ice):

  NAME = u'Card01078'
  SET = card_info.CORE
  NUMBER = 78
  SIDE = card_info.CORP
  FACTION = card_info.NETCORP
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.AP,
      card_info.BARRIER,
  ])
  COST = 8
  IMAGE_SRC = '01078.png'
  STRENGTH = 5

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        do_net_damage.DoNetDamage(game, player, card=self, damage=2),
        subroutines.EndTheRun(self, game)
    ]

  def build_actions(self):
    ice.Ice.build_actions(self)
