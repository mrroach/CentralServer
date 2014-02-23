from csrv.model import actions
from csrv.model import cost
from csrv.model import events
from csrv.model import timing_phases
from csrv.model.actions import subroutines
from csrv.model.cards import card_info
from csrv.model.cards import ice


class LoseCredits(actions.Action):
  DESCRIPTION = 'Pay 3 [credits]'

  def __init__(self, game, player, card=None):
    cost_obj = cost.Cost(game, player, credits=3)
    action.Action.__init__(self, game, player, card=card, cost=cost_obj)
    self._is_mandatory = True
    self.paid = False

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.card.log('The runner pays 3[credits] for Card01090')
    self.paid = True

  def is_usable(self):
    return actions.Action.is_usable(self) and not self.paid


class EndTheRun(actions.Action):
  DESCRIPTION = 'End the run'

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.game.run.end()


class Card01090(ice.Ice):

  NAME = u'Card01090'
  SET = card_info.CORE
  NUMBER = 90
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.CODE_GATE,
  ])
  COST = 8
  IMAGE_SRC = '01090.png'
  STRENGTH = 5

  WHEN_INSTALLED_LISTENS = [
    events.BeginEncounterIce_3_1
  ]

  WHEN_REZZED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'encounter_actions',
  }

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        subroutines.EndTheRun(self.game, self.player)
    ]

  def on_begin_encounter_ice_3_1(self, sender, event):
    self._lose_credits = LoseCredits(self.game, self.game.runner, card=self)

  def build_actions(self):
    ice.Ice.build_actions(self)
    self._end_the_run = EndTheRun(self.game, self.game.runner, card=self)

  def encounter_actions(self):
    if self._lose_credits.is_usable():
      return [self._lose_credits]
    elif self._lose_credits.paid:
      return []
    else:
      return [self._end_the_run]

