"""Trash a trashable card."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors


class TrashOnAccess(action.Action):

  DESCRIPTION = 'Trash an accessed card'
  COST_CLASS = cost.TrashOnAccessCost

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.card.log('The runner trashes %s' % self.card.NAME)
    self.card.trash()
    self.card.on_access_end()

  @property
  def description(self):
    return 'Trash %s' % self.card.NAME
