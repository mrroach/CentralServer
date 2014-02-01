"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import modifiers
from csrv.model import parameters


class StealAgenda(action.Action):

  DESCRIPTION = 'Steal an agenda'
  COST_CLASS = cost.StealAgendaCost

  @property
  def is_mandatory(self):
    if self.card.steal_cost:
      return False
    return True

  def is_usable(self):
    return self.card not in self.game.runner.scored_agendas.cards

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    if self.card.location.parent:
      self.card.location.parent.remove(self.card)
    else:
      self.card.location.remove(self.card)
    self.game.runner.scored_agendas.add(self.card)
    self.game.log('The runner steals %s' % self.card)
    self.card.on_access_end()
    self.trigger_event(events.StealAgenda(self.game, self.player))
