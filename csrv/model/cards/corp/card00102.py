from csrv.model import actions
from csrv.model import timing_phases
from csrv.model import modifiers
from csrv.model.actions import subroutines
from csrv.model.cards import card_info
from csrv.model.cards import ice


class Card00102(ice.Ice):

  NAME = u"Card00102"
  SET = card_info.CORE
  NUMBER = 102
  SIDE = card_info.CORP
  FACTION = card_info.MEATCORP
  INFLUENCE = 3
  UNIQUE = False
  KEYWORDS = set([
      card_info.BARRIER,
  ])
  COST = 10
  IMAGE_SRC = '01102.png'
  STRENGTH = 7
  ADVANCEABLE = True

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpTurnActions: 'installed_actions',
  }

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        subroutines.EndTheRun(self.game, self.player),
        subroutines.EndTheRun(self.game, self.player),
    ]
    self._strength_modifier = modifiers.IceStrengthModifier(
        self.game, 0, card=self)

  def get_advancement_tokens(self):
    return self._advancement_tokens

  def set_advancement_tokens(self, value):
    self._advancement_tokens = value
    self._strength_modifier.set_value(value)

  advancement_tokens = property(get_advancement_tokens, set_advancement_tokens)

  def build_actions(self):
    ice.Ice.build_actions(self)
    self._advance_action = actions.AdvanceCard(self.game, self.player, self)

  def installed_actions(self):
    return [self._advance_action]
