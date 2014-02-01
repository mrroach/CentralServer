"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters


class MulliganAction(action.Action):
  """Return cards to your deck. Shuffle and draw a new starting hand."""

  DESCRIPTION = "Return cards and draw a new starting hand."

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    self.player.draw_starting_hand_and_credits()


