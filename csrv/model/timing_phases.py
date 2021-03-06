"""Phases are parts of the game when particular kinds of actions can be taken.

Each of the main parts of the game are timing phases, and certain card
effects (namely "prevent" or "avoid" type abilities) also cause phases
to come into play.

Each phase gathers up its appropriate choices (e.g. basic actions for
the action phases, rez-a-card operations for abilities phases) and
resolves the choice along with its relevant parameters (such as target
cards, or payment sources).

Quite a few phases will stay in the game's phase queue until something
happens to complete that phase (e.g. running out of clicks, or not having
anything available to rez, or electing not to take an action).
"""

import re
from csrv.model import actions
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object

UNDERSCORE_RE = re.compile(r'\B((?<=[a-z])[A-Z]|[A-Z](?=[a-z]))')


class PhaseMeta(type):
  """A simple metaclass to add the callback name to phase classes."""

  def __new__(mcs, name, bases, new_attrs):

    # ThingHappensPhase.choices_method => 'thing_happens_phase_choices'
    if 'DESCRIPTION' not in new_attrs:
      new_attrs['DESCRIPTION'] = new_attrs['__doc__']
    if 'choices_method' not in new_attrs or not new_attrs['choices_method']:
      new_attrs['choices_method'] = (
          UNDERSCORE_RE.sub(r'_\1', name).lower() + '_choices')
    if 'event' not in new_attrs or not new_attrs['event']:
      new_attrs['event'] = getattr(events, name, None)
    if 'begin_event' not in new_attrs or not new_attrs['begin_event']:
      new_attrs['begin_event'] = getattr(events, 'Begin' + name, None)
    if 'end_event' not in new_attrs or not new_attrs['end_event']:
      new_attrs['end_event'] = getattr(events, 'End' + name, None)
    return type.__new__(mcs, name, bases, new_attrs)


class BasePhase(game_object.GameObject):
  """Base phase for both players."""

  __metaclass__ = PhaseMeta

  DESCRIPTION = None
  NULL_OK = True
  NULL_CHOICE = 'Do nothing'

  begin_event = None
  event = None
  end_event = None

  def __init__(self, game, player, both_players=True):
    game_object.GameObject.__init__(self, game)
    if not both_players:
      self._order = [player]
    elif player == self.game.corp:
      self._order = [self.game.corp, self.game.runner]
    else:
      self._order = [self.game.runner, self.game.corp]
    self.begun = False
    self._choices = []
    self._ended = False
    self._event_emitted = False
    self._begin_event_emitted = False
    self._end_event_emitted = False

  def __str__(self):
    return self.__class__.__name__

  def begin(self):
    self.begun = True
    self._ended = False
    if self.begin_event and not self._begin_event_emitted:
      # pylint: disable=E1102
      self.trigger_event(self.begin_event(self.game, self.player))
      self._begin_event_emitted = True
    if not self._event_emitted and self.event:
      # pylint: disable=E1102
      self.trigger_event(self.event(self.game, self.player))
      self._event_emitted = True

  def end_immediately(self):
    self._ended = True

  def end_phase(self):
    self.begun = False
    self._ended = True
    if not self._end_event_emitted and self.end_event:
      # pylint: disable=E1102
      self.trigger_event(self.end_event(self.game, self.player))
    try:
      self.game.remove_phase(self)
      if self.game.run:
        self.game.run.on_phase_end(self)
    except ValueError:
      pass

  @property
  def player(self):
    if self._order:
      return self._order[0]
    else:
      return None

  def choices(self, refresh=False):
    """Return the list of actions for the current player for this phase."""
    listeners = self.game.choice_providers_for(self.__class__)
    if refresh or not self._choices:
      self._choices = []
      for listener, method in listeners:
        for choice in getattr(listener, method)():
          if choice.player == self.player and choice.is_usable():
            self._choices.append(choice)
    return self._choices

  @property
  def null_choice(self):
    return self.NULL_CHOICE

  @property
  def description(self):
    return self.DESCRIPTION

  def resolve(self, choice, response=None):
    """Perform the given choice, and repeat self phase if more choices exist."""
    if choice:
      choice.resolve(response)
      if self._ended:
        return
      if not self.choices():
        self.next_player()
    else:
      if self.NULL_OK:
        mandatory = [c for c in self.choices() if c.is_mandatory]
        if mandatory:
          return
        else:
          self.next_player()
      elif self.choices():
        raise errors.ChoiceRequiredError(
            '%s: You must choose one of the options' % self)
      else:
        self.next_player()

  def next_player(self):
    """Switch to the next player, and resolve if they have no choices."""
    if self._order:
      del self._order[0]
    if not self._order:
      self.end_phase()
    elif not self.choices():
      self.resolve(None, None)


class CorpGameSetup(BasePhase):
  """The corp draws a starting hand and credits."""
  NULL_CHOICE = 'Keep current hand.'


class CorpTurnAbilities(BasePhase):
  """Corp may rez cards and score agendas; both players may use abilities.

  This phase is made of several sub-phases.
  """
  DESCRIPTION = 'rez/score/abilities window'
  NULL_CHOICE = 'Done using abilities. Pass.'

  def __init__(self, game, player):
    BasePhase.__init__(self, game, player)
    self.round_count = {
        'corp': 0,
        'runner': 0}
    self.acted = False
    self.runner_phase = RunnerUseAbilities(game, game.runner,
                                           both_players=False)
    self.corp_phases = [
        CorpRezCards(game, game.corp, both_players=False),
        CorpScoreAgendas(game, game.corp, both_players=False),
        CorpUseAbilities(game, game.corp, both_players=False),
    ]

  def choices(self, refresh=False):
    """Gather the available choices for self phase.

    Returns:
      list<choice.Choice>
    """
    choices = getattr(self, str(self.player) +'_choices')(refresh=refresh)
    return choices

  def corp_choices(self, refresh=False):
    if not self._choices or refresh:
      self._choices = []
      for phase in self.corp_phases:
        self._choices.extend(phase.choices(refresh=True))
    return self._choices

  def runner_choices(self, refresh=False):
    if not self._choices or refresh:
      self._choices = self.runner_phase.choices(refresh=True)
    return self._choices

  def resolve(self, choice, parameters=None):
    """Perform the given choice, and repeat self phase if more choices exist."""
    if not self._event_emitted and self.event:
      # pylint: disable=E1102
      self.trigger_event(self.event(self.game, self.player))
      self._event_emitted = True
    if choice:
      self.acted = True
      choice.resolve(parameters)
    choices = self.choices(refresh=True)
    if not choices or not choice:
      # player's round ends
      self.round_count[str(self.player)] += 1
      self.next_player()
      if not self.acted and all(self.round_count.values()):
        # everyone has had at least one chance to act
        self.end_phase()
      else:
        self.acted = False
        self.choices(refresh=True)
    #self.game.log('%s chose %s(%s)' % (self.player, choice, parameters))

  def next_player(self):
    """Switch to the next player, and resolve if they have no choices."""
    self._order.reverse()


class CorpRezCards(BasePhase):
  """Corp may rez cards."""


class CorpRezIce(BasePhase):
  """Corp may rez ice."""


class CorpScoreAgendas(BasePhase):
  """Corp may score agendas."""


class CorpUseAbilities(BasePhase):
  """The corp may use abilities."""


class RunnerUseAbilities(BasePhase):
  """The runner may use abilities."""


class CorpTurnBegin(BasePhase):
  """The beginning of the Corp's turn."""


class CorpTurnDraw(BasePhase):
  """The corp's mandatory draw."""


class CorpTurnActions(BasePhase):
  """The corp takes actions."""

  NULL_OK = False

  def __init__(self, game, player):
    BasePhase.__init__(self, game, player, both_players=False)

  def add_abilities_phase(self):
    self.game.insert_phase_before(
        self, CorpTurnAbilities(self.game, self.game.corp))

  def resolve(self, choice, parameters=None):
    BasePhase.resolve(self, choice, parameters)
    if choice and self._choices:
      self.add_abilities_phase()

  def end_phase(self):
    # we have to do self before removing ourselves.
    self.add_abilities_phase()
    BasePhase.end_phase(self)


class CorpTurnDiscard(BasePhase):
  """The corp must discard down to max hand size."""
  NULL_OK = False


class RunnerGameSetup(BasePhase):
  """The runner draws a starting hand and credits."""
  NULL_CHOICE = 'Keep current hand.'


class RunnerTurnAbilities(CorpTurnAbilities):
  """The corp may rez cards; both player may use paid abilities."""
  DESCRIPTION = 'rez/abilities window'

  def __init__(self, game, player):
    BasePhase.__init__(self, game, player)
    self.order = ['runner', 'corp']
    self.round_count = {
        'corp': 0,
        'runner': 0}
    self.acted = False
    self.runner_phase = RunnerUseAbilities(game, player, both_players=False)
    self.corp_phases = [
        CorpRezCards(game, game.corp, both_players=False),
        CorpUseAbilities(game, game.corp, both_players=False),
    ]


class RunnerTurnBegin(BasePhase):
  """The runner's turn begins."""


class RunnerTurnActions(BasePhase):
  """The runner takes actions."""

  NULL_OK = False

  def __init__(self, game, player):
    BasePhase.__init__(self, game, player, both_players=False)

  def add_abilities_phase(self):
    self.game.insert_phase_before(
        self, RunnerTurnAbilities(self.game, self.player))

  def resolve(self, choice, response=None):
    BasePhase.resolve(self, choice, response)
    if choice and self._choices:
      self.add_abilities_phase()

  def end_phase(self):
    self.add_abilities_phase()
    BasePhase.end_phase(self)


class RunnerTurnDiscard(BasePhase):
  """The runner must discard down to max hand size."""
  NULL_OK = False


class RunEvent(BasePhase):
  """Choose a server for the run."""
  NULL_OK = False

  def begin(self):
    BasePhase.begin(self)
    # This is bad. There needs to be a better way
    # this extra click is to cover the cost of making a run.
    self.player.clicks.gain(1)

  def resolve(self, choice, response):
    BasePhase.resolve(self, choice, response)
    if choice:
      self.end_phase()


class ApproachIce_2_1(CorpTurnAbilities):
  """The runner approaches a piece of ice."""
  DESCRIPTION = 'Approaching ice - abilities window'
  # paid abilities

  def __init__(self, game, player, run):
    CorpTurnAbilities.__init__(self, game, player)
    self.order = ['runner', 'corp']
    self.round_count = {
        'corp': 0,
        'runner': 0}
    self.acted = False
    self.runner_phase = RunnerUseAbilities(game, player)
    self.corp_phases = [
        CorpUseAbilities(game, game.corp),
    ]
    self.run = run


class ApproachIce_2_2(BasePhase):
  """The runer approaches a piece of ice."""
  DESCRIPTION = 'Approaching ice - decide whether to continue'
  NULL_OK = False

  def __init__(self, game, player, run):
    BasePhase.__init__(self, game, player, both_players=False)
    self.run = run

  def resolve(self, choice, response=None):
    BasePhase.resolve(self, choice, response)


class ApproachIce_2_3(CorpTurnAbilities):
  """The runer approaches a piece of ice."""
  PHASE_TITLE = 'Approach ice'
  DESCRIPTION = 'Approach ice - ice can be rezzed, rez/abilities window'
  NULL_CHOICE = 'Done rezzing ice/using abilities'

  def __init__(self, game, player, run):
    CorpTurnAbilities.__init__(self, game, player)
    self.order = ['runner', 'corp']
    self.runner_phase = RunnerUseAbilities(game, player)
    self.corp_phases = [
        CorpRezCards(game, game.corp, both_players=False),
        CorpRezIce(game, game.corp, both_players=False),
        CorpUseAbilities(game, game.corp, both_players=False),
    ]
    self.run = run
    self.run.current_ice().on_begin_approach()

  def end_phase(self):
    self.run.current_ice().on_end_approach()
    CorpTurnAbilities.end_phase(self)


class EncounterIce_3(BasePhase):
  """The runner encounters a rezzed piece of ice."""

  def end_phase(self):
    BasePhase.end_phase(self)


class EncounterIce_3_1(BasePhase):
  """The runner encounters a rezzed piece of ice."""
  DESCRIPTION = 'Encounter ice - icebreakers can interact, abilities window'
  NULL_CHOICE = 'Done using icebreakers/abilities. Pass.'

  def __init__(self, game, player, run):
    BasePhase.__init__(self, game, player)
    self.run = run

  def end_phase(self):
    BasePhase.end_phase(self)


class EncounterIce_3_2(BasePhase):
  """The runner encounters a rezzed piece of ice."""
  DESCRIPTION = 'Encounter ice - resolve unbroken subroutines'
  NULL_OK = False

  def __init__(self, game, player, run):
    BasePhase.__init__(self, game, player)
    self.run = run

  def end_phase(self):
    BasePhase.end_phase(self)


class ApproachServer_4_1(CorpTurnAbilities):
  """The runner approaches an attacked server."""

  DESCRIPTION = 'Approach server - rez/abilities window'

  def __init__(self, game, player, run):
    CorpTurnAbilities.__init__(self, game, player)
    self.runner_phase = RunnerUseAbilities(game, player)
    self.corp_phases = [
        CorpUseAbilities(game, game.corp),
    ]
    self.run = run


class ApproachServer_4_2(BasePhase):
  """The runner approaches an attacked server."""

  DESCRIPTION = 'Approaching server - decide whether to continue'
  NULL_OK = False

  def __init__(self, game, player, run):
    BasePhase.__init__(self, game, player)
    self.run = run


class ApproachServer_4_3(CorpTurnAbilities):
  """The runner approaches an attacked server."""

  DESCRIPTION = 'Approaching server - rez/abilities window'

  def __init__(self, game, player, run):
    CorpTurnAbilities.__init__(self, game, player)
    self.runner_phase = RunnerUseAbilities(game, player, both_players=False)
    self.corp_phases = [
        CorpUseAbilities(game, game.corp, both_players=False),
        CorpRezCards(game, game.corp, both_players=False),
    ]
    self.run = run


class ApproachServer_4_4(BasePhase):
  """The runner approaches an attacked server."""

  DESCRIPTION = 'The run is successful'
  NULL_CHOICE = 'Begin access'

  def __init__(self, game, player, run):
    BasePhase.__init__(self, game, player)
    self.run = run

  def begin(self):
    BasePhase.begin(self)
    self.run.successful_run()


class ApproachServer_4_5_Begin(BasePhase):
  """The runner accesses cards in the attacked server."""

  DESCRIPTION = 'Access cards in the attacked server'

  def __init__(self, game, player, run):
    BasePhase.__init__(self, game, player)


class SelectAccessPhase(BasePhase):
  """The runner selects an optional 'instead of accessing' action."""
  DESCRIPTION = 'Choose an option instead of accessing'

  def __init__(self, game, player):
    BasePhase.__init__(self, game, player, both_players=False)

  def resolve(self, choice, response=None):
    BasePhase.resolve(self, choice, response)
    if choice:
      self.end_phase()


class ApproachServer_4_5(BasePhase):
  """The runner accesses cards in the attacked server."""

  DESCRIPTION = 'Access cards in the attacked server'
  NULL_OK = False

  def __init__(self, game, player, run):
    BasePhase.__init__(self, game, player)
    self.run = run
    self._access_initiated = False

  def begin(self):
    BasePhase.begin(self)
    self.game.insert_phase_after(
        self, EndAccess(self.game, self.player))

  def choices(self, refresh=False):
    if not self._access_initiated:
      self.run.access_cards()
      self._access_initiated = True
    return BasePhase.choices(self, refresh=refresh)

  def resolve(self, choice, response=None):
    result = BasePhase.resolve(self, choice, response)
    return result


class EndAccess(BasePhase):
  """All cards have been accessed. The run ends."""

  DESCRIPTION = 'The run ends successfully'
  NULL_CHOICE = 'Complete the run'

  def begin(self):
    BasePhase.begin(self)
    self.game.run = None


class AccessCard(BasePhase):
  """Access a card in a server"""

  DESCRIPTION = 'Access a card'
  NULL_CHOICE = 'Done accessing'

  def __init__(self, game, player, card):
    BasePhase.__init__(self, game, player, both_players=False)
    self.card = card
    self._access_initiated = False

  @property
  def null_choice(self):
    return '%s %s' % (self.NULL_CHOICE, self.card)

  def begin(self):
    BasePhase.begin(self)
    if not self._access_initiated:
      self.card.on_access()
      self._access_initiated  = True

  def resolve(self, choice, params=None):
    BasePhase.resolve(self, choice, params)
    self.card.on_access_end()


class ResolveSubroutine(BasePhase):
  """An ice subroutine resolves."""
  NULL_OK = False

  SHORT_DESC = 'Resolve ice subroutine'
  DESCRIPTION = 'An ice subroutine resolves'

  def __init__(self, game, player, run, subroutine):
    BasePhase.__init__(self, game, player, both_players=False)
    self.run = run
    self.subroutine = subroutine

  def choices(self, refresh=False):
    return [self.subroutine]

  def resolve(self, choice, response=None):
    BasePhase.resolve(self, choice, response)
    if choice:
      self.end_phase()


class TraceCorpBoost(BasePhase):
  """The corp can boost the strength of a trace."""

  NULL_OK = False

  def __init__(self, game, player, trace):
    BasePhase.__init__(self, game, player, both_players=False)
    self.trace = trace

  def resolve(self, choice, response=None):
    BasePhase.resolve(self, choice, response)
    if choice:
      self.end_phase()


class TraceRunnerBoost(BasePhase):
  """The runner can boost the strength of a trace."""

  NULL_OK = False

  def __init__(self, game, player, trace):
    BasePhase.__init__(self, game, player, both_players=False)
    self.trace = trace

  def resolve(self, choice, response=None):
    BasePhase.resolve(self, choice, response)
    if choice:
      self.end_phase()


class ChooseNumCardsToAccess(BasePhase):
  """Choose the number of cards to access in a successful run."""

  def __init__(self, game, player):
    BasePhase.__init__(self, game, player, both_players=False)

  def resolve(self, choice, response=None):
    BasePhase.resolve(self, choice, response)
    if choice:
      self.end_phase()


class TakeDamage(BasePhase):
  """Base class for damage types."""

  def __init__(self, game, player, damage=1):
    BasePhase.__init__(self, game, player, both_players=False)
    self.damage = damage
    self.original_damage = damage

  def resolve(self, choice, response):
    BasePhase.resolve(self, choice, response)
    if not choice and self.damage:
      self.game.runner.take_damage(self.damage)


class TakeBrainDamage(TakeDamage):
  """The runner takes brain damage."""

  def resolve(self, choice, response):
    TakeDamage.resolve(self, choice, response)
    if not choice and self.damage:
      self.game.runner.brain_damage += self.damage

  @property
  def default(self):
    return 'Take %s brain damage' % self.damage


class TakeNetDamage(TakeDamage):
  """The runner takes net damage."""

  @property
  def default(self):
    return 'Take %s net damage' % self.damage


class TakeMeatDamage(TakeDamage):
  """The runner takes meat damage."""

  @property
  def default(self):
    return 'Take %s meat damage' % self.damage


class TakeTags(BasePhase):
  """The runner takes tags."""

  def __init__(self, game, player, tags=1):
    BasePhase.__init__(self, game, player, both_players=False)
    self.tags = tags

  def resolve(self, choice, response):
    BasePhase.resolve(self, choice, response)
    if not choice and self.tags:
      self.game.runner.tags += self.tags


class TrashAProgram(BasePhase):
  """A program is trashed."""

  def __init__(self, game, player, program):
    BasePhase.__init__(self, game, player, both_players=False)
    self.program = program

  def resolve(self, choice, response):
    BasePhase.resolve(self, choice, response)
    if not choice and self.program.is_installed:
      self.program.trash()


class ActivateAbilityChoice(BasePhase):
  """Decide whether to use a card's optional ability."""
  NULL_OK = False

  def __init__(self, game, player, yes_action, no_action, next_phase):
    BasePhase.__init__(self, game, player, both_players=False)
    self.yes_action = yes_action
    self.no_action = no_action
    self.next_phase = next_phase

  def choices(self, refresh=False):
    if not self._choices:
      self._choices = [self.yes_action, self.no_action]
    return self._choices

  def resolve(self, choice, response):
    if not choice:
      raise errors.ChoiceRequiredError('You must choose one of the options')
    if choice == self.yes_action:
      choice.resolve(response)
      if self.next_phase:
        self.game.insert_next_phase(self.next_phase)
        self.next_phase.begin()
      self.end_phase()
    else:
      choice.resolve(response)
      self.end_phase()

class EndOfRun(BasePhase):
  """A sentinel value to anchor run phase insertion."""
  NULL_OK = False  # cause phase to be auto-reaped
  event = events.RunEnds

  def __init__(self, game, player):
    BasePhase.__init__(self, game, player, both_players=False)
