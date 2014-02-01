"""Jack out of a run."""

from csrv.model.actions import action


class JackOut(action.Action):

  DESCRIPTION = 'Jack out of the run'

  def __init__(self, game, player, run, card=None):
    action.Action.__init__(self, game, player, card=card)
    self.run = run

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.game.log('The runner jacks out of the run')
    self.run.jack_out()
