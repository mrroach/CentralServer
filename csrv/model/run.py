from csrv.model import actions
from csrv.model import events
from csrv.model import game_object
from csrv.model import timing_phases


class Run(game_object.GameObject):
  """A class to generate and track phases of a run."""

  LISTENS = [
      events.UninstallIce,
  ]

  def __init__(self, game, server):
    game_object.GameObject.__init__(self, game)
    self.server = server
    self.successful = None

    # A phase to use instead of ApproachServer_4_5
    self.alternate_access_phase_class = None

    self._server_ice = list(reversed(self.server.ice.cards))
    self.runner_position = 0
    self._jack_out_action = actions.JackOut(self.game, self.game.runner, self)
    self._continue_run_action = actions.ContinueRun(
        self.game, self.game.runner, self)
    self._sentinel_phase = timing_phases.EndOfRun(game, self.game.runner)
    self.bypass_ice = False
    # Phases that can replace phase 4.5
    self.optional_access_replacements = []

    self.game.insert_next_phase(self._sentinel_phase)
    self._phases = []

    self.accessed_cards = set()

  def begin(self):
    self.trigger_event(events.RunBegins(self.game, self.game.runner))
    if self._server_ice:
      self.approach_first_ice()
    else:
      self.approach_server()

  def end(self):
    """Immediately end the run. Remove pending phases."""
    self.remove_phases()
    self.unsuccessful_run()

  def on_uninstall_ice(self, sender, event):
    """If the currently encountered ice is trashed, move to the next one."""
    if sender == self.current_ice():
      del self._server_ice[self.runner_position]
      self.remove_phases()
      if self.current_ice():
        self.approach_next_ice()
      else:
        self.approach_server()
    elif sender in self._server_ice:
      current = self.current_ice()
      self._server_ice.remove(sender)
      if current:
        self.runner_position = self._server_ice.index(current)

  def add_phase(self, phase_class):
    """Add a phase game and local phase list."""
    if isinstance(phase_class, timing_phases.BasePhase):
      phase = phase_class
    else:
      phase = phase_class(self.game, self.game.runner, self)
    self.game.insert_phase_before(self._sentinel_phase, phase)
    self._phases.append(phase)

  def add_subroutine_phase(self, subroutine):
    """Add a phase corresponding to an ice subroutine."""
    phase = timing_phases.ResolveSubroutine(
        self.game, self.game.runner, self, subroutine)
    self.game.insert_phase_before(self._sentinel_phase, phase)
    self._phases.append(phase)

  def remove_phases(self):
    """Remove all existing phases from game and local."""
    for phase in list(self._phases):
      phase.end_immediately()
      try:
        self.game.remove_phase(phase)
      except ValueError:
        pass
      self._phases.remove(phase)

  def on_phase_end(self, phase):
    """Callback to handle the end of any run phases."""
    if phase in self._phases:
      self._phases.remove(phase)
    if isinstance(phase, timing_phases.ApproachIce_2_3):
      self.begin_encounter_if_rezzed()
    elif isinstance(phase, timing_phases.EncounterIce_3_1):
      if self.bypass_ice:
        self.bypass_ice = False
        self.pass_ice()
      else:
        self.encounter_subroutines()
    elif isinstance(phase, timing_phases.EncounterIce_3_2):
      self.pass_ice()
    elif isinstance(phase, timing_phases.ApproachServer_4_4):
      self.begin_access()
    elif isinstance(phase, timing_phases.SelectAccessPhase):
      self.game.deregister_choice_provider(
          timing_phases.SelectAccessPhase, self, 'select_access_actions')

  def pass_ice(self):
    """Go to the next phase after phase 3.2 (encounter ice)."""
    self.runner_position += 1
    if len(self._server_ice) > self.runner_position:
      self.approach_next_ice()
    else:
      self.approach_server()

  def approach_first_ice(self):
    """Add phases for approaching the first ice in the server."""
    self.add_phase(timing_phases.ApproachIce_2_1)
    # There's no 2_2 for the first approached ice
    self.add_phase(timing_phases.ApproachIce_2_3)

  def approach_next_ice(self):
    """Add phases for approaching the next ice in the server."""
    self.add_phase(timing_phases.ApproachIce_2_1)
    # There's no certainty that phase 2_3 will happen. We register
    # choices to decide whether to add it.
    self.game.register_choice_provider(
        timing_phases.ApproachIce_2_2, self, 'approach_2_2_actions')
    self.add_phase(timing_phases.ApproachIce_2_2)

  def approach_server(self):
    """Add phases for approaching a server."""
    self.add_phase(timing_phases.ApproachServer_4_1)
    # There's no certainty that phase 4_3 will happen. We register
    # choices to decide whether to add it.
    self.game.register_choice_provider(
        timing_phases.ApproachServer_4_2, self, 'approach_4_2_actions')
    self.add_phase(timing_phases.ApproachServer_4_2)

  def current_ice(self):
    """Return the current ice being encountered."""
    if self.runner_position < len(self._server_ice):
      return self._server_ice[self.runner_position]

  def begin_encounter_if_rezzed(self):
    """Determine whether to encounter ice or pass it."""
    if self.current_ice().is_rezzed:
      self.encounter_ice()
    else:
      self.pass_ice()

  def encounter_ice(self):
    """Begin encounter with the current piece of ice."""
    self.add_phase(timing_phases.EncounterIce_3_1)

  def encounter_subroutines(self):
    """Add phases for encountering a piece of ice."""
    for subroutine in self.current_ice().subroutines:
      if not subroutine.is_broken:
        self.add_subroutine_phase(subroutine)
    # This signals the end of the encounter with this ice
    self.add_phase(timing_phases.EncounterIce_3_2)

  def approach_2_2_actions(self):
    """Actions provided by the run during 2.2 (approach ice)."""
    return [self._jack_out_action, self._continue_run_action]

  def approach_4_2_actions(self):
    """Actions provided by the run during 4.2 (approach server)."""
    return [self._jack_out_action, self._continue_run_action]

  def jack_out(self):
    # Depending on whether we were jacking out on approach of ice
    # or a server, deregister the appropriate things.
    if self.current_ice():
      self.game.deregister_choice_provider(
          timing_phases.ApproachIce_2_2, self, 'approach_2_2_actions')
    else:
      self.game.deregister_choice_provider(
          timing_phases.ApproachServer_4_2, self, 'approach_4_2_actions')
    self.unsuccessful_run()

  def continue_run(self):
    if self.current_ice():
      self.game.deregister_choice_provider(
          timing_phases.ApproachIce_2_2, self, 'approach_2_2_actions')
      self.add_phase(timing_phases.ApproachIce_2_3)
    else:
      self.game.deregister_choice_provider(
          timing_phases.ApproachServer_4_2, self, 'approach_4_2_actions')
      self.add_phase(timing_phases.ApproachServer_4_3)
      self.add_phase(timing_phases.ApproachServer_4_4)

  def begin_access(self):
    """Either insert phase 4.5, or allow alternate access"""
    if self.alternate_access_phase_class:
      self.add_phase(self.alternate_access_phase_class)
    else:
      self.game.register_choice_provider(
          timing_phases.SelectAccessPhase, self, 'select_access_actions')
      select_access_phase = timing_phases.SelectAccessPhase(
          self.game, self.game.runner)
      choices = select_access_phase.choices()
      self.add_phase(select_access_phase)
      if len(choices) == 1:
        select_access_phase.resolve(choices[0], None)

  def select_access_actions(self):
    return [actions.NewTimingPhase(
                self.game, self.game.runner,
                run=self,
                phase_class=timing_phases.ApproachServer_4_5,
                description='Access cards')]

  def access_cards(self):
    """Tell the server to set up access on the appropriate cards."""
    self.server.on_access()

  def unsuccessful_run(self):
    self.successful = False
    self.trigger_event(events.UnsuccessfulRun(self.game, self.game.runner))
    self.game.deregister_listener(events.UninstallIce, self)
    self.game.run = None
    self.game.log('The run is unsuccessful.')

  def successful_run(self):
    self.successful = True
    self.trigger_event(events.SuccessfulRun(self.game, self.game.runner))
    self.game.log('The run is successful.')

  def cancel(self):
    """Cancel the run. It is neither successful or unsuccessful."""
    # canceling only happens before success has been declared
    if self.successful is None:
      self.remove_phases()
      self.game.run = None
      self.game.log('The run was cancelled.')

