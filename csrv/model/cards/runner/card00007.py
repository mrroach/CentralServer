from csrv.model import timing_phases
from csrv.model import actions
from csrv.model import modifiers
from csrv.model.cards import card_info
from csrv.model.cards import program


class Card00007(program.Program):

  NAME = u'Card00007'
  SET = card_info.CORE
  NUMBER = 7
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.FRACTER,
      card_info.ICEBREAKER,
  ])
  COST = 2
  IMAGE_SRC = '01007.png'
  STRENGTH = 2
  MEMORY = 1

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'interact_with_ice_actions',
  }

  def build_actions(self):
    program.Program.build_actions(self)
    self._boost_strength_action = actions.BoostBreakerStrength(
        self.game, self.player, self, strength=1, credits=1)

  def interact_with_ice_actions(self):
    return ([self._boost_strength_action] +
        [actions.BreakBarrierSubroutine(
             self.game, self.player, self, sub, credits=1)
         for sub in self.game.run.current_ice().subroutines])

