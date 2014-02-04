from csrv.model.cards import asset
from csrv.model.cards import card_info


class Card01071(asset.Asset):

  NAME = u'Card01071'
  SET = card_info.CORE
  NUMBER = 71
  SIDE = card_info.CORP
  FACTION = card_info.NETCORP
  INFLUENCE = 1
  UNIQUE = False
  COST = 0
  IMAGE_SRC = '01071.png'
  TRASH_COST = 4

  def build_actions(self):
    asset.Asset.build_actions(self)
