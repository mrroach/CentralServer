from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import ice
from csrv.model import actions
from csrv.model.actions.subroutines import trash_a_program
from csrv.model.actions.subroutines import trace_for_tag_and_brain_damage


class Card00062(ice.Ice):

  NAME = u'Card00062'
  SET = card_info.CORE
  NUMBER = 62
  SIDE = card_info.CORP
  FACTION = card_info.ROBOCORP
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.ROBOMAN,
      card_info.DESTROYER,
      card_info.SENTRY,
      card_info.TRACER,
  ])
  COST = 5
  IMAGE_SRC = '01062.png'
  STRENGTH = 4

  WHEN_REZZED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'break_for_clicks_actions',
  }

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        trash_a_program.TrashAProgram(self.game, self.player),
        trash_a_program.TrashAProgram(self.game, self.player),
        trace_for_tag_and_brain_damage.TraceForTagAndBrainDamage(
            self.game, self.player, 1),
    ]

  def build_actions(self):
    ice.Ice.build_actions(self)

  def _break_for_click(self, subroutine):
    return actions.BreakSubroutine(
        self.game, self.game.runner, self,
        subroutine, credits=0, clicks=1)

  def break_for_clicks_actions(self):
    if self.game.run and self.game.run.current_ice() == self:
      return [self._break_for_click(sub) for sub in self.subroutines]
    return []
