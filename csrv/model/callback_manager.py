"""A callback manager that is copyable/picklable."""

import collections


class Transaction(object):
  """A context manager to prevent new events from firing."""

  def __init__(self, manager):
    self.manager = manager
    self._original_state = self.manager.is_queueing()

  def __enter__(self):
    self.manager.set_queueing(True)

  def __exit__(self, type, value, traceback):
    self.manager.set_queueing(self._original_state)
    if not self.manager.is_queueing():
      self.manager.flush_events()


class CallbackManager(object):
  """A simple callback dispatcher.

  Uses references to the listening object instead of to the object's
  method in order to make it possible to deepcopy the handlers.

  This is done in order to be able to make copies of the game state for
  undo and for running simulations.
  """
  def __init__(self):
    self.handlers = collections.defaultdict(set)
    self._queue_events = False
    self._pending_events = []

  def is_queueing(self):
    return self._queue_events

  def set_queueing(self, val):
    self._queue_events = val

  def transaction(self):
    return Transaction(self)

  def connect(self, event_type, listener):
    """Add a new listener for the given event class."""
    self.handlers[event_type].add(listener)

  def disconnect(self, event_type, listener):
    """Remove a listener."""
    if listener in self.handlers[event_type]:
      self.handlers[event_type].remove(listener)

  def emit(self, event, sender):
    """Send the given event to all listeners."""
    if self._queue_events:
      self._pending_events.append((event, sender))
    else:
      self._emit(event, sender)

  def flush_pending(self):
    for event, sender in self._pending_events:
      self._emit(event, sender)

  def _emit(self, event, sender):
    for listener in list(self.handlers[event.__class__]):
      getattr(listener, event.callback)(sender, event)

  def get(self, event_type):
    """Return all handlers for the event type."""
    return self.handlers[event_type]

