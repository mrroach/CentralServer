from csrv.model import actions
from csrv.model import cost
from csrv.model import events
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import hardware


class Card01023(hardware.Hardware):

  NAME = u'Card01023'
  SET = card_info.CORE
  NUMBER = 23
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 1
  UNIQUE = False
  COST = 1
  IMAGE_SRC = '01023.png'

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnActions: 'expose_actions',
  }

  LISTENS = [
      events.SuccessfulRun,
  ]

  def __init__(self, game, player):
    hardware.Hardware.__init__(self, game, player)
    self.last_successful_hq_run_turn = -1

  def build_actions(self):
    hardware.Hardware.build_actions(self)
    cost_obj = cost.Cost(self.game, self.player, clicks=1, credits=1)
    self._expose_action = actions.ExposeCard(
        self.game, self.player, card=self, cost=cost_obj)

  def expose_actions(self):
    if self.game.runner_turn_count == self.last_successful_hq_run_turn:
      return [self._expose_action]
    else:
      return []

  def on_successful_run(self, sender, event):
    if self.game.run and self.game.run.server == self.game.corp.hq:
      self.last_successful_hq_run_turn = self.game.runner_turn_count
