from csrv.model.actions import trace_boost
from csrv.model import events
from csrv.model import game_object
from csrv.model import timing_phases


class Trace(game_object.GameObject):
  """Initiate a trace and call either success or failure callbacks."""

  PROVIDES_CHOICES_FOR = {
      timing_phases.TraceCorpBoost: 'corp_boost_actions',
      timing_phases.TraceRunnerBoost: 'runner_boost_actions',
  }

  def __init__(self, game, base_strength, initiator, success_cb, failure_cb):
    game_object.GameObject.__init__(self, game)
    self.base_strength = base_strength
    self.corp_total = None
    self.runner_total = None
    self.initiator = initiator
    self.success_cb = success_cb
    self.failure_cb = failure_cb
    self.game.insert_next_phase(
        timing_phases.TraceRunnerBoost(self.game, self.game.runner, self))
    self.game.insert_next_phase(
        timing_phases.TraceCorpBoost(self.game, self.game.corp, self))
    self.game.current_phase().begin()
    self._corp_boost_action = trace_boost.TraceBoost(
        self.game, self.game.corp, self, 'corp_boost_callback')
    self._runner_boost_action = trace_boost.TraceBoost(
        self.game, self.game.runner, self, 'runner_boost_callback')

  def corp_boost_actions(self):
    return [self._corp_boost_action]

  def runner_boost_actions(self):
    return [self._runner_boost_action]

  def runner_boost_callback(self, credits):
    self.runner_total = self.game.runner.link.value + credits
    self.game.deregister_choice_provider(
        timing_phases.TraceRunnerBoost, self, 'runner_boost_actions')
    if credits:
      self.log('The runner boosts link to %s' % self.runner_total)
    else:
      self.log('The runner leaves link at %s' % self.runner_total)
    self.resolve()

  def corp_boost_callback(self, credits):
    self.corp_total = self.base_strength + credits
    self.game.deregister_choice_provider(
        timing_phases.TraceCorpBoost, self, 'corp_boost_actions')
    if credits:
      self.log('The corp boosts the trace to %s' % self.corp_total)
    else:
      self.log('The corp leaves the trace at %s' % self.corp_total)

  def resolve(self):
    if self.corp_total > self.runner_total:
      getattr(self.initiator, self.success_cb)(
          self.corp_total, self.runner_total)
    else:
      getattr(self.initiator, self.failure_cb)(
          self.corp_total, self.runner_total)

