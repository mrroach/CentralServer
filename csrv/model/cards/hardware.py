"""A hardware card."""

from csrv.model import actions
from csrv.model import events
from csrv.model import modifiers
from csrv.model.cards import installable_card
from csrv.model import game_object
from csrv.model import timing_phases
from csrv.model.cards import card_info


class Hardware(installable_card.InstallableCard):

  TYPE = card_info.HARDWARE

  WHEN_IN_HAND_PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnActions: 'install_actions',
  }

  @property
  def cost(self):
    cost = self.COST
    for mod in self.game.modifiers[
        modifiers.HardwareCostModifier].card_scope[self]:
        cost += mod.value
    for mod in self.game.modifiers[
        modifiers.HardwareCostModifier].global_scope:
        cost += mod.value
    return cost

  def build_actions(self):
    installable_card.InstallableCard.build_actions(self)
    self.install_action = actions.InstallHardware(self.game, self.player, self)

  def on_install(self):
    installable_card.InstallableCard.on_install(self)
    self.trigger_event(events.InstallHardware(self.game, self.player))

  def install_actions(self):
    if self.player.clicks.value:
      return [self.install_action]
    return []

  def install_host_targets(self):
    targets = []
    for card in self.game.runner.rig.cards:
      if card.can_host(self):
        targets.append(card)
    return targets
