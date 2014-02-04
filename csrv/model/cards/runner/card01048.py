from csrv.model.cards import card_info
from csrv.model.cards import resource


class Card01048(resource.Resource):

  NAME = u'Card01048'
  SET = card_info.CORE
  NUMBER = 48
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.REMOTE,
  ])
  COST = 0
  IMAGE_SRC = '01048.png'

  def build_actions(self):
    resource.Resource.build_actions(self)
