from csrv.model import actions
from csrv.model import errors
from csrv.model import events
from csrv.model import parameters
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import event


class PerformDrain(actions.Action):
  """Force the corp to lose up to 5[Credits]"""
  DESCRIPTION = 'Choose number of credits to drain'
  REQUEST_CLASS = parameters.NumericChoiceRequest

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if (not response or response.number < 0 or response.number > 5
        or response.number > self.game.corp.credits.value):
      raise errors.InvalidResponse(
          'You must choose a number between 0 and 5 (and less than or equal'
          ' to the number of credits the corp has available)')
    actions.Action.resolve(self, response,
                           ignore_clicks=ignore_clicks,
                           ignore_all_costs=ignore_all_costs)
    self.game.corp.credits.lose(response.number)
    self.game.runner.credits.gain(response.number * 2)
    self.game.runner.tags += 2


class DrainPhase(timing_phases.BasePhase):
  """Force the Corp to lose credits."""

  NULL_OK = False

  def resolve(self, choice, response=None):
    timing_phases.BasePhase.resolve(self, choice, response)
    if choice:
      self.end_phase()


class Card00018(event.Event):

  NAME = u'Card00018'
  SET = card_info.CORE
  NUMBER = 18
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 4
  UNIQUE = False
  KEYWORDS = set([
      card_info.RUN,
      card_info.SABOTAGE,
  ])
  COST = 0
  IMAGE_SRC = '01018.png'

  def build_actions(self):
    event.Event.build_actions(self)

  def play(self):
    event.Event.play(self)
    # TODO(mrroach): update this to handle additional costs
    self.game.register_choice_provider(
        timing_phases.SelectAccessPhase, self, 'drain_actions')
    self.game.register_choice_provider(
        DrainPhase, self, 'perform_drain_actions')
    self.game.register_listener(events.RunEnds, self)
    new_run = self.game.new_run(self.game.corp.hq)
    new_run.begin()

  def on_run_ends(self, sender, event):
    self.game.deregister_listener(events.RunEnds, self)
    self.game.deregister_choice_provider(
        DrainPhase, self, 'perform_drain_actions')
    self.game.deregister_choice_provider(
        timing_phases.SelectAccessPhase, self, 'drain_actions')

  def drain_actions(self):
    return [actions.NewTimingPhase(
        self.game, self.player, phase_class=DrainPhase,
        description='Account drain')]

  def perform_drain_actions(self):
    return [PerformDrain(self.game, self.player)]

