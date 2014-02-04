from csrv.model import modifiers
from csrv.model.cards import card_info
from csrv.model.cards import hardware


class Card01038(hardware.Hardware):

  NAME = u'Card01038'
  SET = card_info.CORE
  NUMBER = 38
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.CHIP,
  ])
  COST = 1
  IMAGE_SRC = '01038.png'

  def build_actions(self):
    hardware.Hardware.build_actions(self)

  def on_install(self):
    hardware.Hardware.on_install(self)
    self._memory_mod = modifiers.MemorySize(self.game, 1)

  def on_uninstall(self):
    hardware.Hardware.on_uninstall(self)
    self._memory_mod.remove()
