"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class MakeARunAction(action.Action):

  DESCRIPTION = 'Make a run.'
  COST_CLASS = cost.MakeARunCost

  def __init__(self, game, player, server):
    action.Action.__init__(self, game, player)
    self.server = server

  @property
  def description(self):
    return 'Make a run on ' + str(self.server)

  def __str__(self):
    return self.description

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.game.log('The runner makes a run on %s' % self.server)
    new_run = self.game.new_run(self.server)
    new_run.begin()
