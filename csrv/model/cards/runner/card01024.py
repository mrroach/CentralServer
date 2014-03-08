from csrv.model import events
from csrv.model import modifiers
from csrv.model.cards import card_info
from csrv.model.cards import hardware


class Card01024(hardware.Hardware):

  NAME = u'Card01024'
  SET = card_info.CORE
  NUMBER = 24
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 3
  UNIQUE = True
  KEYWORDS = set([
      card_info.CONSOLE,
  ])
  COST = 3
  IMAGE_SRC = '01024.png'

  WHEN_INSTALLED_LISTENS = [
      events.SuccessfulRun
  ]

  def build_actions(self):
    hardware.Hardware.build_actions(self)

  def on_install(self):
    hardware.Hardware.on_install(self)
    self._memory_mod = modifiers.MemorySize(self.game, 1)

  def on_uninstall(self):
    hardware.Hardware.on_uninstall(self)
    self._memory_mod.remove()

  def on_successful_run(self, sender, event):
    self.log('The runner gains 1[Credit] from Card01024')
    self.game.runner.credits.gain(1)
