from csrv.model import modifiers
from csrv.model.cards import card_info
from csrv.model.cards import upgrade


class Card01066(upgrade.Upgrade):

  NAME = u'Card01066'
  SET = card_info.CORE
  NUMBER = 66
  SIDE = card_info.CORP
  FACTION = card_info.ROBOCORP
  INFLUENCE = 1
  UNIQUE = False
  COST = 2
  IMAGE_SRC = '01066.png'
  TRASH_COST = 2

  def __init__(self, game, player):
    upgrade.Upgrade.__init__(self, game, player)
    self.modifier = None

  def build_actions(self):
    upgrade.Upgrade.build_actions(self)

  def on_rez(self):
    self.modifier = modifiers.IceStrengthModifier(
        self.game, 1, server=self.location.parent)

  def on_derez(self):
    if self.modifier:
      self.modifier.remove()
      self.modifier = None
