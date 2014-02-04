"""An ice card."""

from csrv.model import actions
from csrv.model import events
from csrv.model import game_object
from csrv.model import modifiers
from csrv.model import parameters
from csrv.model.cards import card_base
from csrv.model import timing_phases


class Ice(card_base.CardBase):

  TYPE = 'Ice'
  REZZABLE = True

  WHEN_IN_HAND_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpTurnActions: 'install_actions',
  }

  WHEN_APPROACHED_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpRezIce: 'rez_actions',
  }
  WHEN_APPROACHED_LISTENS = []

  WHEN_INSTALLED_LISTENS = [
      events.EndEncounterIce_3_2,
  ]

  def __init__(self, game, player):
    card_base.CardBase.__init__(self, game, player)
    self.subroutines = []

  @property
  @modifiers.modifiable(modifiers.IceStrengthModifier)
  def strength(self):
    return self.STRENGTH

  @property
  @modifiers.modifiable(modifiers.IceRezCostModifier)
  def cost(self):
    return self.COST

  def build_actions(self):
    self.install_action = actions.InstallIce(self.game, self.player, self)
    self._rez_action = actions.RezIce(self.game, self.player, self)

  def install_actions(self):
    if self.player.clicks.value:
      return [self.install_action]
    return []

  def rez_actions(self):
    if not self.is_rezzed:
      return [self._rez_action]
    return []

  def on_begin_approach(self):
    self._setup_choices('APPROACHED')

  def on_end_approach(self):
    self._teardown_choices('APPROACHED')

  def on_end_encounter_ice_3_2(self, event, sender):
    for sub in self.subroutines:
      sub.is_broken = False

  def on_rez(self):
    card_base.CardBase.on_rez(self)
    self.trigger_event(events.RezIce(self.game, self.player))

  def on_install(self):
    card_base.CardBase.on_install(self)
    self.trigger_event(events.InstallIce(self.game, self.player))

  def on_uninstall(self):
    card_base.CardBase.on_uninstall(self)
    self.trigger_event(events.UninstallIce(self.game, self.player))

  def _break_for_click(self, subroutine):
    return actions.BreakSubroutine(
        self.game, self.game.runner, self,
        subroutine, credits=0, clicks=1)
