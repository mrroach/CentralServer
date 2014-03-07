"""Master class for tracking and advancing game state."""

import collections
import copy
import random
from csrv.model import callback_manager
from csrv.model import events
from csrv.model import locations
from csrv.model import modifiers
from csrv.model import player
from csrv.model import run
from csrv.model import timing_phases


class Game(object):
  """Tracks game state."""

  def __init__(self, corp_deck, runner_deck):

    self.choice_count = 0
    self.corp_turn_count = 0
    self.runner_turn_count = 0

    self.corp_wins = False
    self.runner_wins = False
    self.runner_flatlined = False

    # Don't use guessable ids
    self._next_id = random.randint(0, 200)
    self._id_map = {}
    self.exposed_ids = set()

    self.active_player = None
    self._choice_providers = collections.defaultdict(set)
    self._initial_events = callback_manager.CallbackManager()
    self._final_events = self._initial_events
    self._response_targets = collections.defaultdict(set)
    self.modifiers = collections.defaultdict(modifiers.ModifierScopes)

    self.run = None
    self.runner = player.RunnerPlayer(self, runner_deck)
    self.corp = player.CorpPlayer(self, corp_deck)
    self.banished = locations.Banished(self, None)

    self.timing_phases = [
        timing_phases.CorpGameSetup(self, self.corp),
        timing_phases.RunnerGameSetup(self, self.runner),
    ]
    self.current_phase().begin()
    self._log = []

  def trigger_event(self, event, sender):
    """Send an event to all listeners.

    Args:
      event: events.Event, An instance of an event.
      sender: game_object.GameObject, The object emitting this event.
    """
    self._initial_events.emit(event, sender)

  def register_listener(self, event_type, listener):
    """Start listening to a type of event.

    Args:
      event_type: A subclass of events.Event.
      listener: game_object.GameObject, An object that
          implements event_type.callback
    """
    self._initial_events.connect(event_type, listener)

  def deregister_listener(self, event_type, listener):
    """Stop listening to a type of event.

    Args:
      event_type: A subclass of events.Event.
      listener: game_object.GameObject, An object that
          implements event_type.callback
    """
    self._initial_events.disconnect(event_type, listener)

  def register_choice_provider(self, timing_phase, provider, method):
    """Register an object that provides choices for a particular timing phase.

    Timing phases are any part of the game that require (or could potentially
    require) a choice to be made by one or more players. Examples would be
    the corp or runner's main action phases.

    They are also used to represent effects that need to be explained to the
    player, but don't necessarily require a response. Examples of this would be
    the firing of a subroutine.

    Args:
      timing_phase: A subclass of timing_phases.Phase the phase in which to
          provide choices.
      provider: game_object.GameObject, The object which provides choices.
      method: str, The name of the method to call on provider to get the list
          of choices.
    """
    self._choice_providers[timing_phase].add((provider, method))

  def deregister_choice_provider(self, timing_phase, provider, method):
    """Deregister an object that is currently providing choices.

    Args:
      timing_phase: timing_phases.Phase, The phase in which to provide choices.
      provider: game_object.GameObject, The object which provides choices.
      method: str, The name of the method to call on provider to get the list
          of choices.
    """
    try:
      self._choice_providers[timing_phase].remove((provider, method))
    except KeyError:
      pass

  def register_response_target(self, request_class, field, target):
    """Declare that an object is a valid target for a particular request.

    Args:
      request_class: parameters.Request subclass.
      field: str, Field of the response that target is valid for.
      target: game_object.GameObject, Object that is a valid target.
    """
    self._response_targets[(request_class, field)].add(target)

  def deregister_response_target(self, request_class, field, target):
    """Remove a previously declared response target.

    Args:
      request_class: parameters.Request subclass.
      field: str, Field of the response.
      target: game_object.GameObject, Object that is no longer a valid target.
    """
    self._response_targets[(request_class, field)].remove(target)

  def valid_response_targets_for(self, request_class, field):
    return self._response_targets[(request_class, field)]

  def new_run(self, server):
    """Create a new run object and associate it with this game.

    Args:
       server: csrv.model.locations.server
    Returns:
       The new run.
    """
    self.run = run.Run(self, server)
    return self.run

  def expose_card(self, card):
    """Add a card to the list of exposed ids."""
    # This is going to have to get more complicated to support prevention
    self.exposed_ids.add(card.game_id)

  def new_id(self):
    """Return a new game object id.

    Returns:
      int, A unique id.
    """
    new_id = str(self._next_id)
    self._next_id += 1
    return new_id

  def register_game_object(self, game_obj, old_id=None):
    """Store a weak reference to a game object.

    Args:
      game_obj: game_object.GameObject, object with game_id
      old_id: The previous id for this object. Will be deregistered.
    """
    if old_id is not None and old_id in self._id_map:
      del self._id_map[old_id]
    self._id_map[game_obj.game_id] = game_obj

  def get_game_object(self, game_id):
    """Resolve and return the game object matching game_id."""
    return self._id_map.get(game_id)

  def resolve_current_phase(self, choice, parameters):
    """Resolve the first phase on the queue using the given choice.

    Args:
      choice: choices.Choice, An action/ability to perform.
      parameters: Targets or payments for the action/ability.
    """
    phase = self.current_phase()
    phase.resolve(choice, parameters)
    self.choice_count += 1
    # it could be a new phase
    phase = self.current_phase()
    player = phase.player
    while True:
      previous_phase = phase
      previous_player = player
      if not phase.begun:
        phase.begin()
      # Phases have no way to know that they should just remove themselves
      choices = self.current_phase().choices(refresh=True)
      if not choices and not self.current_phase().NULL_OK:
        self.current_phase().next_player()
      phase = self.current_phase()
      player = phase.player
      if phase == previous_phase and player == previous_player:
        break

  def current_phase(self):
    """Return the next available event without removing it from the queue.

    Returns:
      timing_phases.Phase
    """
    if not self.timing_phases:
      self._change_player()
    return self.timing_phases[0]

  def remove_phase(self, phase):
    """Remove the given phase from the set of phases.

    Args:
      phase: timing_phases.Phase
    """
    self.timing_phases.remove(phase)

  def insert_next_phase(self, phase, position=0):
    """Add a new phase to the (by default, top of) timing phases.

    Args:
      phase: timing_phases.Phase
      position: int, Where to place the phase
    """
    self.timing_phases.insert(position, phase)

  def append_phase(self, phase):
    """Add a new phase to the end of timing phases.

    Args:
      phase: timing_phases.Phase
    """
    self.timing_phases.append(phase)

  def insert_phase_before(self, before, phase):
    """Insert a phase just before another phase."""
    position = self.timing_phases.index(before)
    self.insert_next_phase(phase, position)

  def insert_phase_after(self, after, phase):
    """Insert a phase just after another phase."""
    position = self.timing_phases.index(after)
    self.insert_next_phase(phase, position + 1)

  def choice_providers_for(self, event):
    """Return objects which provide choices for the given event.

    Args:
      event: events.Event, The sort of event to look up.
    Returns:
      set<(object, method)>, Action provider methods.
    """
    return self._choice_providers.get(event, [])

  def runner_flatline(self):
    """The runner took too much damage and died."""
    self.runner_flatlined = True
    self.corp_wins = True

  def corp_win(self):
    self.log('The corp wins')
    self.corp_wins = True

  def runner_win(self):
    self.log('The runner wins')
    self.runner_wins = True

  def _change_player(self):
    """Switch players between runner and corp."""
    if self.active_player == self.corp:
      if self.corp_turn_count:
        self.log("The corp's turn ends")
        self.trigger_event(
            events.CorpTurnEnd(self, self.corp),
            self.corp)
      self.active_player = self.runner
      self._add_runner_turn_phases()
      self.runner_turn_count += 1
    else:
      if self.runner_turn_count:
        self.log("The runner's turn ends")
        self.trigger_event(
          events.RunnerTurnEnd(self, self.runner),
          self.runner)
      self.active_player = self.corp
      self._add_corp_turn_phases()
      self.corp_turn_count += 1

  def _add_corp_turn_phases(self):
    """Add normal timing phases for a corp turn."""
    for event_class in [
        timing_phases.CorpTurnAbilities,
        timing_phases.CorpTurnBegin,
        timing_phases.CorpTurnDraw,
        timing_phases.CorpTurnActions,
        # Abilities phase is added by the action phase
        timing_phases.CorpTurnDiscard,
        # There should technically be a non-agenda ability window
        # here, but one comes immedately at the beginning of the
        # runner turn, so I don't care.
        ]:
      self.timing_phases.append(event_class(self, self.corp))

  def _add_runner_turn_phases(self):
    """Add normal timing phases for a runner turn."""
    for event_class in [
        timing_phases.RunnerTurnAbilities,
        timing_phases.RunnerTurnBegin,
        timing_phases.RunnerTurnAbilities,
        timing_phases.RunnerTurnActions,
        timing_phases.RunnerTurnDiscard,
        timing_phases.RunnerTurnAbilities,
        ]:
      self.timing_phases.append(event_class(self, self.runner))

  def log(self, message, game_id=None):
    """Store a log of an event.

    messages will be visible to both players, so should not have secret info.

    Args:
      message: str, The message to log.
      game_id: str, The id of the game object logging the event.
    """
    self._log.append({'message': message, 'game_id': game_id})

