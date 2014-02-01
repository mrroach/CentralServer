from csrv.model.actions.subroutines import do_net_damage
from csrv.model.cards import card_info
from csrv.model.cards import ice


class Card00077(ice.Ice):

  NAME = u'Card00077'
  SET = card_info.CORE
  NUMBER = 77
  SIDE = card_info.CORP
  FACTION = card_info.NETCORP
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.AP,
      card_info.SENTRY,
  ])
  COST = 4
  IMAGE_SRC = '01077.png'
  STRENGTH = 3

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        do_net_damage.DoNetDamage(self.game, self.player, self, 3),
    ]

  def build_actions(self):
    ice.Ice.build_actions(self)
