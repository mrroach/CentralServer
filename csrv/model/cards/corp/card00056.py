from csrv.model.cards import asset
from csrv.model.cards import card_info
from csrv.model import events
from csrv.model import actions
from csrv.model import pool


class Card00056(asset.Asset):

  NAME = 'Card00056'
  SET = card_info.CORE
  SUBTYPES = ['Advertisement']
  COST = 4
  TRASH_COST = 3
  FACTION = 'ROBOCORP'
  INFLUENCE = 2

  NUMBER = 56
  IMAGE_SRC = '01056.png'

  LISTENS = [
      events.CorpTurnBegin,
  ]

  def __init__(self, game, player):
    asset.Asset.__init__(self, game, player)
    self.pool = None

  @property
  def credits(self):
    if self.pool:
      return self.pool.value
    return 0

  def on_rez(self):
    asset.Asset.on_rez(self)
    self.pool = pool.CreditPool(self.game, self.player, 12)

  def on_derez(self):
    asset.Asset.on_derez(self)
    self.pool = None

  def on_corp_turn_begin(self, sender, event):
    if self.is_rezzed:
      if self.pool and self.pool.value >= 3:
        self.pool.lose(3)
        self.player.credits.gain(3)
      if self.pool and self.pool.value < 3:
        self.pool = None
        self.trash()
