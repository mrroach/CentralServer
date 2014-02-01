from csrv.model import actions
from csrv.model import modifiers
from csrv.model.cards import card_info
from csrv.model.cards import upgrade


class Card00105(upgrade.Upgrade):

  NAME = u'Card00105'
  SET = card_info.CORE
  NUMBER = 105
  SIDE = card_info.CORP
  FACTION = card_info.MEATCORP
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.FACILITY,
  ])
  COST = 2
  IMAGE_SRC = '01105.png'
  TRASH_COST = 3

  def __init__(self, game, player):
    upgrade.Upgrade.__init__(self, game, player)
    self.modifier = None

  def build_actions(self):
    upgrade.Upgrade.build_actions(self)
    self.install_action = actions.InstallUpgrade(
        self.game, self.player, self, server=self.player.hq)

  def on_rez(self):
    self.modifier = modifiers.CorpMaxHandSize(self.game, 2)

  def on_derez(self):
    if self.modifier:
      self.modifier.remove()
      self.modifier = None
