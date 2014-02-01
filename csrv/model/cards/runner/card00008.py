from csrv.model import cost
from csrv.model import actions
from csrv.model import events
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import program


class Card00008Cost(cost.Cost):
  def can_pay(self):
    return True if self.card.virus_counters else False

  def pay(self, response=None, ignore_clicks=False):
    self.card.virus_counters -= 1


class Card00008(program.Program):

  NAME = u'Card00008'
  SET = card_info.CORE
  NUMBER = 8
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.VIRUS,
  ])
  COST = 1
  MEMORY = 1
  IMAGE_SRC = '01008.png'

  WHEN_INSTALLED_LISTENS = [
      events.ApproachServer_4_4,
  ]

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'interact_with_ice_actions'
  }

  def build_actions(self):
    program.Program.build_actions(self)
    self._reduce_ice_strength_action = actions.ReduceIceStrength(
        self.game, self.player, self, -1,
        Card00008Cost(self.game, self.player, self))

  def on_approach_server_4_4(self, sender, event):
    if self.game.run.server in self.game.corp.centrals:
      self.virus_counters += 1

  def interact_with_ice_actions(self):
    return [self._reduce_ice_strength_action]

