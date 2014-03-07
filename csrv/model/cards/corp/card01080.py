from csrv.model import appropriations
from csrv.model import pool
from csrv.model.cards import card_info
from csrv.model.cards import identity


class Card01080(identity.Identity):

  NAME = u'Card01080'
  SET = card_info.CORE
  NUMBER = 80
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  UNIQUE = False
  KEYWORDS = set([
      card_info.MEGACORP,
  ])
  IMAGE_SRC = '01080.png'

  def __init__(self, game, player):
    identity.Identity.__init__(self, game, player)
    self.pool = pool.CreditPool(
        game, player, 2,
        appropriation=set([appropriations.PERFORM_TRACE]),
        recurring=True)
    player.credit_pools.add(self.pool)

  def build_actions(self):
    identity.Identity.build_actions(self)

  @property
  def credits(self):
    return self.pool.value

