"""Break a subroutine with an icebreaker."""

from csrv.model import appropriations
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters
from csrv.model.actions import action
from csrv.model.cards import card_info


class BreakSubroutine(action.Action):

  DESCRIPTION = 'Break a subroutine'
  REQUIRED_KEYWORDS = set()

  def __init__(self, game, player, card, subroutine, credits=1, clicks=0):
    cost_obj = cost.SimpleCost(game, player, credits=credits, clicks=clicks)
    action.Action.__init__(self, game, player, cost=cost_obj)
    self.card = card
    if isinstance(subroutine, list):
      self.subroutines = subroutine
    else:
      self.subroutines = [subroutine]

    if card_info.ICEBREAKER in self.card.KEYWORDS:
      self.cost.appropriations.append(appropriations.USE_ICEBREAKERS)

  def is_usable(self):
    if self.REQUIRED_KEYWORDS:
      if not self.REQUIRED_KEYWORDS & self.game.run.current_ice().KEYWORDS:
        return False
    return (self.cost.can_pay() and
        self.card.strength >= self.game.run.current_ice().strength and not
        self.subroutines_broken())

  def subroutines_broken(self):
    return any([s.is_broken for s in self.subroutines])

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.card.log('The runner breaks "%s" with %s' %
                  (', '.join(str(s) for s in self.subroutines), self.card))
    for subroutine in self.subroutines:
      subroutine.is_broken = True

  @property
  def description(self):
    message = 'Break "%s" with %s' % (
        ','.join(str(s) for s in self.subroutines), self.card)
    costs = []
    if self.cost.clicks():
      costs.append(','.join(['[click]' for i in range(self.cost.clicks())]))
    if self.cost.credits():
      costs.append('%s [credits]' % self.cost.credits())
    if costs:
      message = '%s: %s' % (','.join(costs), message)
    return message
