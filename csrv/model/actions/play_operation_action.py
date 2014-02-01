"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class PlayOperationAction(action.Action):

  DESCRIPTION = '[click]: Play an operation'
  COST_CLASS = cost.OperationCost

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.player.hq.remove(self.card)
    self.card.is_faceup = True
    self.card.play()
    self.card.log('The corp plays %s' % self.card)
    self.player.archives.add(self.card)

  @property
  def description(self):
    return 'Play %s' % self.card.NAME


