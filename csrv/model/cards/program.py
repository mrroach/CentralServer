"""A program card."""

from csrv.model import actions
from csrv.model import events
from csrv.model.cards import card_base
from csrv.model import game_object
from csrv.model import modifiers
from csrv.model import parameters
from csrv.model import timing_phases
from csrv.model.cards import card_info


class Program(card_base.CardBase):

  TYPE = card_info.PROGRAM
  REZZABLE = False

  WHEN_INSTALLED_LISTENS = [
      events.PurgeVirusCounters,
  ]

  WHEN_IN_HAND_PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnActions: 'install_actions',
  }
  HOST_ON = []

  @property
  @modifiers.modifiable(modifiers.ProgramStrengthModifier, server_scope=False)
  def strength(self):
    return self.STRENGTH

  @property
  @modifiers.modifiable(modifiers.ProgramCostModifier, server_scope=False)
  def cost(self):
    return self.COST

  def build_actions(self):
    self.install_action = actions.InstallProgram(self.game, self.player, self)

  def install_actions(self):
    return [self.install_action]

  def install_host_targets(self):
    targets = []
    for card in self.game.runner.rig.cards:
      if card.can_host(self):
        targets.append(card)
    return targets

  def install_programs_to_trash_targets(self):
    return [c for c in self.game.runner.rig.cards if isinstance(c, Program)]

  def on_purge_virus_counters(self, sender, event):
    self.virus_counters = 0

  def on_install(self):
    card_base.CardBase.on_install(self)
    self.trigger_event(events.InstallProgram(self.game, self.player))
    self.game.register_response_target(
        parameters.InstallProgramRequest, 'programs_to_trash', self)

  def on_uninstall(self):
    card_base.CardBase.on_uninstall(self)
    self.game.deregister_response_target(
        parameters.InstallProgramRequest, 'programs_to_trash', self)
