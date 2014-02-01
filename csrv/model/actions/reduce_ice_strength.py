"""Reduce the strength of a piece of ice."""

from csrv.model import appropriations
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import modifiers
from csrv.model import parameters
from csrv.model.actions import action
from csrv.model.cards import card_info


class ReduceIceStrength(action.Action):

  DESCRIPTION = 'Currently encounterd ice has -1 strength'

  def __init__(self, game, player, card, strength, cost_obj):
    action.Action.__init__(self, game, player, cost=cost_obj)
    self.card = card
    self.strength = strength
    if card_info.ICEBREAKER in self.card.KEYWORDS:
        self.cost.appropriations.append(appropriations.USE_ICEBREAKERS)

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    modifiers.IceStrengthModifier(
        self.game, self.strength, until=events.EndEncounterIce_3_2,
        card=self.game.run.current_ice())

  @property
  def description(self):
    return 'Give -1 strength to %s' % self.game.run.current_ice()


