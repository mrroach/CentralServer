"""Boost the strength of an icebreaker."""

from csrv.model.actions import action
from csrv.model import appropriations
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import modifiers
from csrv.model import parameters


class BoostBreakerStrength(action.Action):

  DESCRIPTION = '+1 strength'

  def __init__(self, game, player, card, strength, credits=1,
               until=events.EndEncounterIce_3_2):
    cost_obj = cost.SimpleCost(game, player, credits=credits)
    action.Action.__init__(self, game, player, cost=cost_obj)
    self.until = until
    self.card = card
    self.strength = strength
    self.cost.appropriations.append(appropriations.USE_ICEBREAKERS)

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    # Boost strength until this ice is no longer being encountered
    self.card.log('The runner gives %s strength to %s' %
                  (self.strength, self.card.NAME))
    modifiers.ProgramStrengthModifier(
        self.game, self.strength, until=self.until,
        card=self.card)

  @property
  def description(self):
    return 'Give %s strength to %s' % (self.strength, self.card.NAME)


