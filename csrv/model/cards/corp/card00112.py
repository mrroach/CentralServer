from csrv.model.cards import card_info
from csrv.model.cards import ice
from csrv.model.actions.subroutines import trace_for_tag


class Card00112(ice.Ice):

  NAME = u'Card00112'
  SET = card_info.CORE
  NUMBER = 112
  SIDE = card_info.CORP
  FACTION = card_info.NEUTRAL
  INFLUENCE = 0
  UNIQUE = False
  KEYWORDS = set([
      card_info.OBSERVER,
      card_info.SENTRY,
      card_info.TRACER,
  ])
  COST = 1
  IMAGE_SRC = '01112.png'
  STRENGTH = 4

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        trace_for_tag.TraceForTag(game, player, base_strength=3)
    ]
