from csrv.model import actions
from csrv.model import cost
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import program


class ReduceIceStrength(actions.ReduceIceStrength):

  def is_usable(self):
    return (actions.ReduceIceStrength.is_usable(self) and
            self.card.strength >= self.game.run.current_ice().strength)


class BreakSubroutine(actions.BreakSubroutine):

  def is_usable(self):
    return (actions.BreakSubroutine.is_usable(self) and
            self.game.run.current_ice().strength <= 0)


class Card00013(program.Program):

  NAME = u'Card00013'
  SET = card_info.CORE
  NUMBER = 13
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.AI,
      card_info.ICEBREAKER,
  ])
  COST = 1
  IMAGE_SRC = '01013.png'
  STRENGTH = 1
  MEMORY = 1

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'interact_with_ice_actions',
  }

  def build_actions(self):
    program.Program.build_actions(self)
    self._boost_strength_action = actions.BoostBreakerStrength(
        self.game, self.player, self, strength=1, credits=1)
    cost_obj = cost.SimpleCost(self.game, self.player, credits=1)
    self._reduce_ice_strength_action = ReduceIceStrength(
        self.game, self.player, self, strength=-1, cost_obj=cost_obj)

  def interact_with_ice_actions(self):
    subroutine_actions = [
        BreakSubroutine(self.game, self.player, self, sub, credits=3)
        for sub in self.game.run.current_ice().subroutines
    ]
    return [
        self._boost_strength_action,
        self._reduce_ice_strength_action,
        ] + subroutine_actions
