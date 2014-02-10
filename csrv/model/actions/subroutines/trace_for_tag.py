from csrv.model.actions.subroutines import trace


class TraceForTag(trace.Trace):
  DESCRIPTION = 'Trace - if successful, give the runner 1 tag.'

  def on_success(self, corp_total, runner_total):
    self.game.insert_next_phase(
        timing_phases.TakeTags(self.game, self.game.runner, 1))

  @property
  def description(self):
    return 'Trace %s - if successful, give the runner 1 tag.' % (
        self.base_strength)
