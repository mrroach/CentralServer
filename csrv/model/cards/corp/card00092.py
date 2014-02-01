from csrv.model import modifiers
from csrv.model.cards import card_info
from csrv.model.cards import upgrade


class Card00092(upgrade.Upgrade):

  NAME = u'Card00092'
  SET = card_info.CORE
  NUMBER = 92
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  INFLUENCE = 3
  UNIQUE = False
  KEYWORDS = set([
      card_info.REGION,
  ])
  COST = 6
  IMAGE_SRC = '01092.png'
  TRASH_COST = 5

  def __init__(self, game, player):
    upgrade.Upgrade.__init__(self, game, player)
    self.modifier = None

  def build_actions(self):
    upgrade.Upgrade.build_actions(self)

  def on_rez(self):
    self.modifier = modifiers.AgendaAdvancementRequirement(
        self.game, -1, server=self.location.parent)

  def on_derez(self):
    if self.modifier:
      self.modifier.remove()
      self.modifier = None
