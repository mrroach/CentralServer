import itertools

from csrv.model import actions
from csrv.model import events
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import program


class Card00042(program.Program):

  NAME = u'Card00042'
  SET = card_info.CORE
  NUMBER = 42
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.FRACTER,
      card_info.ICEBREAKER,
  ])
  COST = 5
  IMAGE_SRC = '01042.png'
  STRENGTH = 3
  MEMORY = 2

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'interact_with_ice_actions',
  }

  def build_actions(self):
    program.Program.build_actions(self)
    self._boost_strength_action = actions.BoostBreakerStrength(
        self.game, self.player, self, strength=1, credits=1,
        until=events.RunEnds)

  def _subroutine_combinations(self):
    # Yeah, this is gross. nobody uses this card, do they? :-(
    unbroken = [s for s in self.game.run.current_ice().subroutines
                if not s.is_broken]
    subs = (list(itertools.combinations(unbroken, 2)) +
            list(itertools.combinations(unbroken, 1)))
    return subs

  def interact_with_ice_actions(self):
    return ([self._boost_strength_action] +
          [actions.BreakBarrierSubroutine(
               self.game, self.player, self, list(subs), credits=2)
           for subs in self._subroutine_combinations()])

