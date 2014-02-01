"""A program card."""

from csrv.model import actions
from csrv.model import events
from csrv.model.cards import card_base
from csrv.model import game_object
from csrv.model import modifiers
from csrv.model import parameters
from csrv.model import timing_phases


class Program(card_base.CardBase):

  TYPE = 'Program'
  REZZABLE = False

  WHEN_INSTALLED_LISTENS = [
      events.PurgeVirusCounters,
  ]

  WHEN_IN_HAND_PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnActions: 'install_actions',
  }
  HOST_ON = []

  @property
  def strength(self):
    strength = self.STRENGTH
    for mod in self.game.modifiers[
        modifiers.ProgramStrengthModifier].card_scope[self]:
        strength += mod.value
    for mod in self.game.modifiers[
        modifiers.ProgramStrengthModifier].global_scope:
        strength += mod.value
    return strength

  @property
  def cost(self):
    cost = self.COST
    for mod in self.game.modifiers[
        modifiers.ProgramCostModifier].card_scope[self]:
        cost += mod.value
    for mod in self.game.modifiers[
        modifiers.ProgramCostModifier].global_scope:
        cost += mod.value
    return cost

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
