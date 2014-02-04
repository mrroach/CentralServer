from csrv.model.actions.subroutines import do_net_damage
from csrv.model.cards import card_info
from csrv.model.cards import ice


class NetDamageAndTrash(do_net_damage.DoNetDamage):
  DESCRIPTION = 'Do 1 net damage. Trash Card01076.'

  def resolve(self, response=None):
    do_net_damage.DoNetDamage.resolve(self, response=response)
    self.card.trash()


class Card01076(ice.Ice):

  NAME = u'Card01076'
  SET = card_info.CORE
  NUMBER = 76
  SIDE = card_info.CORP
  FACTION = card_info.NETCORP
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.AP,
      card_info.TRAP,
  ])
  COST = 0
  IMAGE_SRC = '01076.png'
  STRENGTH = 2

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        NetDamageAndTrash(self.game, self.player, card=self, damage=1),
    ]

  def build_actions(self):
    ice.Ice.build_actions(self)
