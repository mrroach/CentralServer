"""Continue a run."""

from csrv.model.actions import action


class ContinueRun(action.Action):

  DESCRIPTION = 'Continue the run'

  def __init__(self, game, player, run):
    action.Action.__init__(self, game, player)
    self.run = run

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.run.continue_run()
