from csrv.model.cards import card_info
from csrv.model.cards import resource


class Card01032(resource.Resource):

  NAME = u'Card01032'
  SET = card_info.CORE
  NUMBER = 32
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.CONNECTION,
  ])
  COST = 1
  IMAGE_SRC = '01032.png'

  def build_actions(self):
    resource.Resource.build_actions(self)
