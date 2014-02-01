from csrv.model import modifiers
from csrv.model.cards import card_info
from csrv.model.cards import upgrade


class Card00079(upgrade.Upgrade):

  NAME = u'Card00079'
  SET = card_info.CORE
  NUMBER = 79
  SIDE = card_info.CORP
  FACTION = card_info.NETCORP
  INFLUENCE = 2
  UNIQUE = True
  KEYWORDS = set([
      card_info.SYSOP,
      card_info.UNORTHODOX,
  ])
  COST = 1
  IMAGE_SRC = '01079.png'
  TRASH_COST = 3

  def __init__(self, game, player):
    upgrade.Upgrade.__init__(self, game, player)
    self.modifier = None

  def build_actions(self):
    upgrade.Upgrade.build_actions(self)

  def on_rez(self):
    upgrade.Upgrade.on_rez(self)
    self.modifier = modifiers.IceRezCostModifier(
        self.game, -2, server=self.location.parent)

  def on_derez(self):
    if self.modifier:
      self.modifier.remove()
      self.modifier = None
