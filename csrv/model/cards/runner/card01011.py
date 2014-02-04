from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import program


class Card01011(program.Program):

  NAME = u'Card01011'
  SET = card_info.CORE
  NUMBER = 11
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.ICEBREAKER,
      card_info.KILLER,
  ])
  COST = 3
  IMAGE_SRC = '01011.png'
  STRENGTH = 3
  MEMORY = 1

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'interact_with_ice_actions',
  }

  def build_actions(self):
    program.Program.build_actions(self)

  def interact_with_ice_actions(self):
    return [actions.BreakSentrySubroutine(self.game, self.player, self, sub)
            for sub in self.game.run.current_ice().subroutines]
