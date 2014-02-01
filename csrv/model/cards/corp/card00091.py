from csrv.model import modifiers
from csrv.model.cards import card_info
from csrv.model.cards import upgrade


class Card00091(upgrade.Upgrade):

  NAME = u'Card00091'
  SET = card_info.CORE
  NUMBER = 91
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  INFLUENCE = 2
  UNIQUE = False
  COST = 1
  IMAGE_SRC = '01091.png'
  TRASH_COST = 1

  def __init__(self, game, player):
    upgrade.Upgrade.__init__(self, game, player)
    self.modifier = None

  def build_actions(self):
    upgrade.Upgrade.build_actions(self)

  def on_rez(self):
    self.modifier = modifiers.StealAgendaCost(
        self.game, 5, server=self.location.parent)

  def on_derez(self):
    if self.modifier:
      self.modifier.remove()
      self.modifier = None
