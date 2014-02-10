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
    if 'description' not in new_attrs:
      new_attrs['description'] = new_attrs['__doc__']
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

  NULL_OK = True
  NULL_NAME = 'Do nothing'

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
      self.trigger_event(self.begin_event(self.game, self.player))
      self._begin_event_emitted = True
    if not self._event_emitted and self.event:
      self.trigger_event(self.event(self.game, self.player))
      self._event_emitted = True

  def end_immediately(self):
    self._ended = True

  def end_phase(self):
    self.begun = False
    self._ended = True
    if not self._end_event_emitted and self.end_event:
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


class OldBasePhase(game_object.PlayerObject):
  """Base timing phase."""

  __metaclass__ = PhaseMeta

  NULL_OK = True
  NULL_NAME = 'Do nothing'

  def __init__(self, game, player):
    game_object.PlayerObject.__init__(self, game, player)
    self.begun = False
    self._ended = False
    self._choices = None
    self._event_emitted = False
    self._begin_event_emitted = False
    self._end_event_emitted = False

  def __str__(self):
    return self.__class__.__name__

  def begin(self):
    self.begun = True
    self._ended = False
    if self.begin_event and not self._begin_event_emitted:
      self.trigger_event(self.begin_event(self.game, self.player))
      self._begin_event_emitted = True
    if not self._event_emitted and self.event:
      self.trigger_event(self.event(self.game, self.player))
      self._event_emitted = True

  def choices(self, refresh=False):
    """Gather the available choices for self phase.

    Returns:
      list<choice.Choice>
    """
    if not self._choices or refresh:
      listeners = self.game.choice_providers_for(self.__class__)
      self._choices = []
      for listener, method in listeners:
        for choice in getattr(listener, method)():
          if choice.is_usable():
            self._choices.append(choice)
    return self._choices

  def clear_choices(self):
    """Clear the choices for self phase. Needed whenever game state changes."""
    self._choices = None

  def resolve(self, choice, parameters=None):
    """Perform the given choice, and repeat self phase if more choices exist."""
    if choice:
      choice.resolve(parameters)
      if self._ended:
        # The choice somehow killed this phase.
        self._choices = None
        return
      if not self.choices(refresh=True):
        self.end_phase()
    else:
      if self.NULL_OK:
        mandatory = [o for o in self.choices() if o.is_mandatory]
        if mandatory:
          # player has passed on all optional choices, mandatory ones must still
          # be handled. probably need to catch self and stick to only mandatory
          # choices from there on out
          self._choices = mandatory
        else:
          self.end_phase()
      elif self._choices:
        raise errors.ChoiceRequiredError(
            '%s: You must choose one of the options' % self)
      else:
        self.end_phase()

  def end_immediately(self):
    self._ended = True

  def end_phase(self):
    self.begun = False
    self._ended = True
    if not self._end_event_emitted and self.end_event:
      self.trigger_event(self.end_event(self.game, self.player))
    try:
      self.game.remove_phase(self)
      if self.game.run:
        self.game.run.on_phase_end(self)
    except ValueError:
      pass


class CorpGameSetup(BasePhase):
  """The corp draws a starting hand and credits."""

  NULL_NAME = 'Keep current hand.'


class CorpTurnAbilities(BasePhase):
  """Corp may rez cards and score agendas; both players may use abilities.

  This phase is made of several sub-phases.
  """
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

  @property
  def description(self):
    if str(self.player) == 'corp':
      return 'Rez cards, score agendas, use abilities'
    else:
      return 'Use abilities'

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
  """The corp draws a starting hand and credits."""


class RunnerTurnAbilities(CorpTurnAbilities):
  """The corp may rez cards; both player may use paid abilities."""

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
  # The runner jacks out or continues (can't jack out on first approached)

  NULL_OK = False

  def __init__(self, game, player, run):
    BasePhase.__init__(self, game, player)
    self.run = run

  def resolve(self, choice, response=None):
    BasePhase.resolve(self, choice, response)


class ApproachIce_2_3(CorpTurnAbilities):
  """The runer approaches a piece of ice."""
  # Approached ice can be rezzed, paid abilities can be used, non-ice cards rezzed
  # If rezzed, go to 3. if unrezzed and more ice, go to 2, else go to 6

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
  # 'When encountered' conditionals happen here

  def end_phase(self):
    BasePhase.end_phase(self)


class EncounterIce_3_1(BasePhase):
  """The runner encounters a rezzed piece of ice."""
  # Icebreakers can interact, paid abilities can be used

  SHORT_DESC = 'Encounter ice: interact'
  DESCRIPTION = 'Icebreakers can interact, paid abilities can be used'

  def __init__(self, game, player, run):
    BasePhase.__init__(self, game, player)
    self.run = run

  def end_phase(self):
    BasePhase.end_phase(self)


class EncounterIce_3_2(BasePhase):
  """The runner encounters a rezzed piece of ice."""
  # Resolve all unbroken subroutines. either run ends (go to 6) or more ice (go to 2)
  # or no more ice (go to 4)

  SHORT_DESC = 'Encounter ice'
  DESCRIPTION = 'The runner encounters a rezzed piece of ice.'

  def __init__(self, game, player, run):
    BasePhase.__init__(self, game, player)
    self.run = run

  def end_phase(self):
    BasePhase.end_phase(self)


class ApproachServer_4_1(CorpTurnAbilities):
  """The runner approaches an attacked server."""

  SHORT_DESC = 'Abilities may be used'
  DESCRIPTION = 'Approach server: abilities may be used, cards may be rezzed.'
  DEFAULT = 'Do not use abilities'

  def __init__(self, game, player, run):
    CorpTurnAbilities.__init__(self, game, player)
    self.runner_phase = RunnerUseAbilities(game, player)
    self.corp_phases = [
        CorpUseAbilities(game, game.corp),
    ]
    self.run = run


class ApproachServer_4_2(BasePhase):
  """The runner approaches an attacked server."""

  SHORT_DESC = 'Approach server'
  DESCRIPTION = 'Approach server: The runner decides whether to continue.'

  NULL_OK = False

  def __init__(self, game, player, run):
    BasePhase.__init__(self, game, player)
    self.run = run


class ApproachServer_4_3(CorpTurnAbilities):
  """The runner approaches an attacked server."""

  SHORT_DESC = 'Approach server'
  DESCRIPTION = 'Approach server: abilities may be used, cards may be rezzed.'
  DEFAULT = 'Do not use abilities'

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

  SHORT_DESC = 'The run is successful.'
  DESCRIPTION = 'The run is successful.'

  def __init__(self, game, player, run):
    BasePhase.__init__(self, game, player)
    self.run = run

  def begin(self):
    BasePhase.begin(self)
    self.run.successful_run()


class ApproachServer_4_5_Begin(BasePhase):
  """The runner accesses cards in the attacked server."""

  SHORT_DESC = 'Begin access'
  DESCRIPTION = 'The runner accesses cards in the attacked server.'

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
  # if the runner accesses an agenda, they steal it
  # if they access a trashable card, they can trash it
  # if there's something with an on-access effect, it happens

  SHORT_DESC = 'Choose cards to access'
  DESCRIPTION = 'The runner accesses cards in the attacked server.'
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

  SHORT_DESC = 'The run ends'
  DESCRIPTION = 'The run ends successfully.'

  def begin(self):
    BasePhase.begin(self)
    self.game.run = None


class AccessCard(BasePhase):
  """Access a card in a server"""

  SHORT_DESC = 'Access a card'
  DESCRIPTION = 'The runner accesses a card in the server.'

  def __init__(self, game, player, card):
    BasePhase.__init__(self, game, player, both_players=False)
    self.card = card
    self._access_initiated = False

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
  DESCRIPTION = 'An ice subroutine resolves.'

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
