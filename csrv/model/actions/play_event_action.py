"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class PlayEventAction(action.Action):

  DESCRIPTION = '[click]: Play an event'
  COST_CLASS = cost.EventCost

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.player.grip.remove(self.card)
    self.card.is_faceup = True
    self.card.play()
    self.card.trash()
    self.game.log('The runner plays %s' % self.card.NAME, self.card.game_id)

  @property
  def description(self):
    return 'Play %s' % self.card.NAME


