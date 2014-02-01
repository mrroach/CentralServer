from csrv.model import actions
from csrv.model import events
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import program


class Card00046(program.Program):

  NAME = u'Card00046'
  SET = card_info.CORE
  NUMBER = 46
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.ICEBREAKER,
      card_info.KILLER,
  ])
  COST = 3
  IMAGE_SRC = '01046.png'
  STRENGTH = 1
  MEMORY = 1

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'interact_with_ice_actions',
  }

  def build_actions(self):
    program.Program.build_actions(self)
    self._boost_strength_action = actions.BoostBreakerStrength(
        self.game, self.player, self, strength=1, credits=1,
        until=events.RunEnds)

  def interact_with_ice_actions(self):
    return ([self._boost_strength_action] +
        [actions.BreakSentrySubroutine(
             self.game, self.player, self, sub, credits=2)
         for sub in self.game.run.current_ice().subroutines])
