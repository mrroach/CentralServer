"""Trash a program."""

from csrv.model.actions import action
from csrv.model import timing_phases
from csrv.model import errors


class TrashAProgram(action.Action):

  DESCRIPTION = 'Trash a card'

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.game.insert_next_phase(
        timing_phases.TrashAProgram(self.game, self.game.runner, self.card))

  @property
  def description(self):
    return 'Trash %s' % self.card.NAME
