from csrv.model import events
from csrv.model.cards import card_info
from csrv.model.cards import identity


class Card01001(identity.RunnerIdentity):

  NAME = u'Card01001'
  SET = card_info.CORE
  NUMBER = 1
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  UNIQUE = False
  KEYWORDS = set([
      card_info.G_MOD,
  ])
  BASE_LINK = 0
  IMAGE_SRC = '01001.png'

  LISTENS = [
      events.InstallProgram,
  ]

  def build_actions(self):
    identity.RunnerIdentity.build_actions(self)

  def on_install_program(self, sender, event):
    if card_info.VIRUS in sender.KEYWORDS:
      self.game.corp.rnd.pop().trash()  # lulz
      self.log('The corp trashes the top card of R&D '
               'because the runner installed a virus')

