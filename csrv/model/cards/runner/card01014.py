from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import program


class Card01014(program.Program):

  NAME = u'Card01014'
  SET = card_info.CORE
  NUMBER = 14
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.DECODER,
      card_info.ICEBREAKER,
  ])
  COST = 5
  IMAGE_SRC = '01014.png'
  STRENGTH = 3
  MEMORY = 1

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'interact_with_ice_actions',
  }

  def build_actions(self):
    program.Program.build_actions(self)

  def interact_with_ice_actions(self):
    return [actions.BreakCodeGateSubroutine(
                self.game, self.player, self, sub, credits=0)
            for sub in self.game.run.current_ice().subroutines]

