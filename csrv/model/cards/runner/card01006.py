from csrv.model.cards import card_info
from csrv.model.cards import hardware
from csrv.model import modifiers
from csrv.model import events


class Card01006(hardware.Hardware):

  NAME = u'Card01006'
  SET = card_info.CORE
  NUMBER = 6
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 2
  UNIQUE = True
  KEYWORDS = set([
      card_info.CONSOLE,
  ])
  COST = 3
  IMAGE_SRC = '01006.png'

  WHEN_INSTALLED_LISTENS = [
      events.InstallProgram,
  ]

  def build_actions(self):
    hardware.Hardware.build_actions(self)

  def on_install(self):
    hardware.Hardware.on_install(self)
    self._memory_mod = modifiers.MemorySize(self.game, 2)

  def on_uninstall(self):
    hardware.Hardware.on_uninstall(self)
    self._memory_mod.remove()

  def on_install_program(self, sender, event):
    if card_info.VIRUS in sender.KEYWORDS:
      sender.virus_counters += 1

