from csrv.model.cards import card_info
from csrv.model.cards import resource


class Card00030(resource.Resource):

  NAME = u'Card00030'
  SET = card_info.CORE
  NUMBER = 30
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.LOCATION,
  ])
  COST = 2
  IMAGE_SRC = '01030.png'

  def build_actions(self):
    resource.Resource.build_actions(self)
