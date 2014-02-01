"""The runner takes brain damage."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import modifiers
from csrv.model import parameters


class TakeBrainDamage(action.Action):

  DESCRIPTION = 'Take brain damage'

  def __init__(self, game, player, card, dmg=1, callback_name=None):
    action.Action.__init__(self, game, player, card)
    self.dmg = dmg
    self._is_mandatory = True
    self.callback_name = callback_name

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.game.runner.take_damage(1)
    self.game.runner.brain_damage += 1
    if self.callback_name:
      getattr(self.card, self.callback_name)()

  @property
  def description(self):
    return 'Take %d brain damage from %s' % (self.dmg, self.card)
