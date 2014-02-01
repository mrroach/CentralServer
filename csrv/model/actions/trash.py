"""Trash a trashable card."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors


class Trash(action.Action):

  DESCRIPTION = 'Trash a card'

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    if self.player == self.game.runner:
      self.card.is_faceup = True
    self.card.trash()

  @property
  def description(self):
    return 'Trash %s' % self.card.NAME
