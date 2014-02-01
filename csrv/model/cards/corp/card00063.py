from csrv.model.cards import card_info
from csrv.model.cards import ice
from csrv.model.actions import subroutines
from csrv.model.actions.subroutines import do_brain_damage
from csrv.model import timing_phases


class Card00063(ice.Ice):

  NAME = u'Card00063'
  SET = card_info.CORE
  NUMBER = 63
  SIDE = card_info.CORP
  FACTION = card_info.ROBOCORP
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.AP,
      card_info.ROBOMAN,
      card_info.CODE_GATE,
  ])
  COST = 3
  IMAGE_SRC = '01063.png'
  STRENGTH = 3

  WHEN_REZZED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'break_for_clicks_actions',
  }

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        do_brain_damage.DoBrainDamage(self.game, self.player, self),
        subroutines.EndTheRun(self.game, self.player, self),
    ]

  def build_actions(self):
    ice.Ice.build_actions(self)

  def break_for_clicks_actions(self):
    if self.game.run and self.game.run.current_ice() == self:
      return [self._break_for_click(sub) for sub in self.subroutines]
    return []
