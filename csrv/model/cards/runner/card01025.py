from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import program


class Card01025(program.Program):

  NAME = u'Card01025'
  SET = card_info.CORE
  NUMBER = 25
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.FRACTER,
      card_info.ICEBREAKER,
  ])
  COST = 3
  IMAGE_SRC = '01025.png'
  STRENGTH = 1
  MEMORY = 1

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'interact_with_ice_actions',
  }

  def build_actions(self):
    program.Program.build_actions(self)
    self._boost_strength_action = actions.BoostBreakerStrength(
        self.game, self.player, self, strength=3, credits=2)

  def interact_with_ice_actions(self):
    return ([self._boost_strength_action] +
        [actions.BreakBarrierSubroutine(
             self.game, self.player, self, sub, credits=2)
         for sub in self.game.run.current_ice().subroutines])
