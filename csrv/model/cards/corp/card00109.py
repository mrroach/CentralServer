from csrv.model.cards import asset
from csrv.model import events
from csrv.model.cards import card_info


class Card00109(asset.Asset):

  NAME = u'Card00109'
  SET = card_info.CORE
  NUMBER = 109
  SIDE = card_info.CORP
  FACTION = card_info.NEUTRAL
  INFLUENCE = 0
  UNIQUE = False
  KEYWORDS = set([
      card_info.ADVERTISEMENT,
  ])
  COST = 2
  IMAGE_SRC = '01109.png'
  TRASH_COST = 4

  WHEN_REZZED_LISTENS = [
      events.CorpTurnBegin,
  ]

  def build_actions(self):
    asset.Asset.build_actions(self)

  def on_corp_turn_begin(self, sender, event):
    self.game.corp.credits.gain(1)
