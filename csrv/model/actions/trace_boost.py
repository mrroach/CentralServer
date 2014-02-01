from csrv.model.actions import action
from csrv.model import appropriations
from csrv.model import parameters
from csrv.model import cost
from csrv.model import errors


class TraceBoost(action.Action):
  """The player may boost the trace."""

  DESCRIPTION = 'Boost a trace'
  REQUEST_CLASS = parameters.VariableCreditCostRequest

  def __init__(self, game, player, trace, callback):
    cost_obj = cost.Cost(
        game, player, appropriations=[appropriations.PERFORM_TRACE])
    action.Action.__init__(self, game, player, cost=cost_obj)
    self.trace = trace
    self.callback = callback

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if response.credits is None or response.credits < 0:
      raise errors.InvalidResponse('You must boost by a positive number.')
    self.cost.add_credits(response.credits)
    if not self.cost.can_pay():
      raise errors.InvalidResponse(
          'You do not have %s credits' % response.credits)
    self.cost.pay()
    getattr(self.trace, self.callback)(response.credits)
