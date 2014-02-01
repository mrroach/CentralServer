from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import program


class Card00027(program.Program):

  NAME = u'Card00027'
  SET = card_info.CORE
  NUMBER = 27
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.ICEBREAKER,
      card_info.KILLER,
  ])
  COST = 4
  IMAGE_SRC = '01027.png'
  STRENGTH = 0
  MEMORY = 1

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'interact_with_ice_actions',
  }

  def build_actions(self):
    program.Program.build_actions(self)
    self._boost_strength_action = actions.BoostBreakerStrength(
        self.game, self.player, self, strength=5, credits=3)

  def interact_with_ice_actions(self):
    return ([self._boost_strength_action] +
        [actions.BreakSentrySubroutine(
             self.game, self.player, self, sub, credits=1)
         for sub in self.game.run.current_ice().subroutines])
