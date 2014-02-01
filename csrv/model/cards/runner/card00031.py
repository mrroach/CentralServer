from csrv.model.cards import card_info
from csrv.model.cards import resource


class Card00031(resource.Resource):

  NAME = u'Card00031'
  SET = card_info.CORE
  NUMBER = 31
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.CONNECTION,
      card_info.SEEDY,
  ])
  COST = 0
  IMAGE_SRC = '01031.png'

  def build_actions(self):
    resource.Resource.build_actions(self)
