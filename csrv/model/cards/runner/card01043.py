from csrv.model import actions
from csrv.model import events
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import program


class Card01043(program.Program):

  NAME = u'Card01043'
  SET = card_info.CORE
  NUMBER = 43
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 3
  UNIQUE = False
  KEYWORDS = set([
      card_info.DECODER,
      card_info.ICEBREAKER,
  ])
  COST = 4
  IMAGE_SRC = '01043.png'
  STRENGTH = 2
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
        [actions.BreakCodeGateSubroutine(
             self.game, self.player, self, sub, credits=1)
         for sub in self.game.run.current_ice().subroutines])
