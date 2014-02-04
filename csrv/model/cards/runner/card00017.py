from csrv.model import events
from csrv.model.cards import card_info
from csrv.model.cards import identity


class Card00017(identity.Identity):

  NAME = u'Card00017'
  SET = card_info.CORE
  NUMBER = 17
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  UNIQUE = False
  KEYWORDS = set([
      card_info.CYBORG,
  ])
  BASE_LINK = 0
  IMAGE_SRC = '01017.png'

  LISTENS = [
      events.SuccessfulRun
  ]

  def __init__(self, game, player):
    identity.Identity.__init__(self, game, player)
    self.ability_used_on_turn = None

  def build_actions(self):
    identity.Identity.build_actions(self)

  def on_successful_run(self, sender, event):
    if self.game.run and self.game.run.server == self.game.corp.hq:
      if not self.ability_used_on_turn == self.game.runner_turn_count:
        self.log('The runner gains 2[Credits] for a successful run on HQ')
        self.ability_used_on = self.game.runner_turn_count
        self.player.credits.gain(2)
