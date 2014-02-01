from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import ice
from csrv.model import actions
from csrv.model.actions.subroutines import do_brain_damage
from csrv.model.actions import subroutines


class Card00061(ice.Ice):

  NAME = u'Card00061'
  SET = card_info.CORE
  NUMBER = 61
  SIDE = card_info.CORP
  FACTION = card_info.ROBOCORP
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.AP,
      card_info.BARRIER,
      card_info.ROBOMAN,
  ])
  COST = 8
  IMAGE_SRC = '01061.png'
  STRENGTH = 6

  WHEN_REZZED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'break_for_clicks_actions',
  }

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        do_brain_damage.DoBrainDamage(self.game, self.player),
        subroutines.EndTheRun(self.game, self.player),
        subroutines.EndTheRun(self.game, self.player),
    ]

  def build_actions(self):
    ice.Ice.build_actions(self)

  def break_for_clicks_actions(self):
    if self.game.run and self.game.run.current_ice() == self:
      return [self._break_for_click(sub) for sub in self.subroutines]
    return []
