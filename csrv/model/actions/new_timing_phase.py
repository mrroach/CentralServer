from csrv.model.actions import action


class NewTimingPhase(action.Action):
  """Insert a new timing phase."""

  def __init__(self, game, player, card=None, cost=None,
               phase_class=None, phase=None, run=None,
               description=None):
    action.Action.__init__(self, game, player, card=card, cost=cost)
    self.phase_class = phase_class
    self.phase = phase
    self.run = run
    self._description = description

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(self, response,
                          ignore_clicks=ignore_clicks,
                          ignore_all_costs=ignore_all_costs)
    if self.phase:
      phase = self.phase
      if self.run:
        return self.run.add_phase(phase)
    else:
      if self.run:
        return self.run.add_phase(self.phase_class)
      else:
        phase = self.phase_class(self.game, self.player)
    self.game.insert_next_phase(phase)

  @property
  def description(self):
    return self._description
