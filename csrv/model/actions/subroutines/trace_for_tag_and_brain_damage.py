from csrv.model.actions.subroutines import trace
from csrv.model import timing_phases


class TraceForTagAndBrainDamage(trace.Trace):
  DESCRIPTION = ('Trace - if successful, give the runner 1 tag and do '
                 '1 brain damage.')

  def on_success(self, corp_total, runner_total):
    self.game.runner.tags += 1
    self.game.add_phase(
        timing_phases.TakeBrainDamage(self.game, self.game.runner, 1))

  @property
  def description(self):
    return ('Trace %s - if successful, give the runner 1 tag '
            'and do 1 brain damage.' % self.base_strength)
