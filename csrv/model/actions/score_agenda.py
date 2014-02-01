"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class ScoreAgenda(action.Action):

  DESCRIPTION = 'Score an agenda'

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.card.log('The corp scores %s' % self.card)
    self.card.score()
    self.trigger_event(events.ScoreAgenda(self.game, self.player))

