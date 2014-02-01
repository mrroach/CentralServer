from csrv.model.actions.subroutines import subroutine
from csrv.model import trace


class Trace(subroutine.Subroutine):

  def __init__(self, game, player, base_strength=3, card=None):
    subroutine.Subroutine.__init__(self, game, player, card=card)
    self.base_strength = base_strength

  def resolve(self, response=None):
    trace.Trace(self.game, self.base_strength, self, 'on_success', 'on_failure')

  def on_success(self, corp_total, runner_total):
    pass

  def on_failure(self, corp_total, runner_total):
    pass
