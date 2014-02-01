from csrv.model import appropriations
from csrv.model.cards import card_info
from csrv.model.cards import hardware
from csrv.model import pool


class Card00005(hardware.Hardware):

  NAME = u'Card00005'
  SET = card_info.CORE
  NUMBER = 5
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.CHIP,
  ])
  COST = 2
  IMAGE_SRC = '01005.png'

  def __init__(self, game, player):
    hardware.Hardware.__init__(self, game, player)
    self.pool = None

  @property
  def credits(self):
    if self.pool:
      return self.pool.value
    return 0

  def build_actions(self):
    hardware.Hardware.build_actions(self)

  def on_install(self):
    hardware.Hardware.on_install(self)
    self.pool = pool.CreditPool(self.game, self.player, 1,
        appropriation=set([appropriations.INSTALL_VIRUSES,
          appropriations.USE_ICEBREAKERS]), recurring=True)
    self.player.credit_pools.add(self.pool)

  def on_uninstall(self):
    self.pool.remove()
    self.player.credit_pools.remove(self.pool)
