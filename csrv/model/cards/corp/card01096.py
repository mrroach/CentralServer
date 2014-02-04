from csrv.model.cards import asset
from csrv.model.cards import card_info


class Card01096(asset.Asset):

  NAME = u'Card01096'
  SET = card_info.CORE
  NUMBER = 96
  SIDE = card_info.CORP
  FACTION = card_info.MEATCORP
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.TRANSACTION,
  ])
  COST = 0
  IMAGE_SRC = '01096.png'
  TRASH_COST = 3

  def build_actions(self):
    asset.Asset.build_actions(self)
