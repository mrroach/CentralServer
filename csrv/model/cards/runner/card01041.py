from csrv.model import actions
from csrv.model import appropriations
from csrv.model import modifiers
from csrv.model import pool
from csrv.model.cards import card_info
from csrv.model.cards import hardware


class Card01041(hardware.Hardware):

  NAME = u'Card01041'
  SET = card_info.CORE
  NUMBER = 41
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 2
  UNIQUE = True
  KEYWORDS = set([
      card_info.CONSOLE,
  ])
  COST = 9
  IMAGE_SRC = '01041.png'

  def __init__(self, game, player):
    hardware.Hardware.__init__(self, game, player)
    self.pool = None
    self._memory_mod = None

  @property
  def credits(self):
    if self.pool:
      return self.pool.value
    return 0

  def build_actions(self):
    hardware.Hardware.build_actions(self)

  def on_install(self):
    hardware.Hardware.on_install(self)
    self._memory_mod = modifiers.MemorySize(self.game, 2)
    self.player.link.gain(2)
    self.pool = pool.CreditPool(
        self.game, self.player, 2,
        appropriation=set([appropriations.USE_ICEBREAKERS]),
        recurring=True)
    self.player.credit_pools.add(self.pool)

  def on_uninstall(self):
    hardware.Hardware.on_uninstall(self)
    self._memory_mod.remove()
    self.player.link.lose(2)
    self.pool.remove()
    self.player.credit_pools.remove(self.pool)
