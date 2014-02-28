"""Modifications to strength, cost, advancement requirement, etc."""

import collections
from functools import wraps
from csrv.model import game_object
from csrv.model import events

# It might make sense for the modifiers to be independent of the card
# so that they can handle hierarchy themselves
#
#
# ModifierDurations = [
#   'END_OF_ENCOUNTER',
#   'END_OF_RUN',
#   'END_OF_TURN',
#   'PARENT_CARD_TRASHED',


class ModifierScopes(object):
  def __init__(self):
    self.global_scope = set()
    self.server_scope = collections.defaultdict(set)
    self.card_scope = collections.defaultdict(set)


def modifiable(modifier_class, card_scope=True,
               server_scope=True, global_scope=True):
  """A decorator to allow easy creation of modified properties."""

  def wrap_method(method):
    @wraps(method)
    def wrapper(self):
      value = method(self)
      if card_scope:
        for mod in self.game.modifiers[modifier_class].card_scope[self]:
          value += mod.value
      if server_scope:
        for mod in self.game.modifiers[
            modifier_class].server_scope[self.location.parent]:
          value += mod.value
      if global_scope:
        for mod in self.game.modifiers[modifier_class].global_scope:
          value += mod.value
      return value
    return wrapper
  return wrap_method


class Modifier(game_object.GameObject):
  """A (usually numeric) modification to normally-static values."""

  EVENT = None

  def __init__(self, game, value, until=None, server=None, card=None):
    game_object.GameObject.__init__(self, game)
    self.value = value
    self.server = server
    self.card = card
    self.until = until

    if self.card:
      # We will automatically remove modifiers when associated card goes away
      self.game.register_listener(events.UninstallCard, self)
      self.card_scope[self.card].add(self)
    elif self.server:
      self.server_scope[self.server].add(self)
    else:
      self.global_scope.add(self)
    if until:
      setattr(self, until.callback, self.on_removal_event)
      self.game.register_listener(until, self)
    if self.EVENT:
      # pylint: disable=E1102
      self.trigger_event(self.EVENT(self.game, None))

  @property
  def card_scope(self):
    return self.game.modifiers[self.__class__].card_scope

  @property
  def server_scope(self):
    return self.game.modifiers[self.__class__].server_scope

  @property
  def global_scope(self):
    return self.game.modifiers[self.__class__].global_scope

  def increase(self, amt):
    self.value += amt
    if self.EVENT:
      # pylint: disable=E1102
      self.trigger_event(self.EVENT(self.game, None))

  def decrease(self, amt):
    self.value -= amt
    if self.EVENT:
      # pylint: disable=E1102
      self.trigger_event(self.EVENT(self.game, None))

  def set_value(self, amt):
    self.value = amt
    if self.EVENT:
      # pylint: disable=E1102
      self.trigger_event(self.EVENT(self.game, None))

  def remove(self):
    if self.until:
      self.game.deregister_listener(self.until, self)
    try:
      if self.card:
        self.game.deregister_listener(events.UninstallCard, self)
        self.card_scope[self.card].remove(self)
      elif self.server:
        self.server_scope[self.server].remove(self)
      else:
        self.global_scope.remove(self)
      if self.EVENT:
        # pylint: disable=E1102
        self.trigger_event(self.EVENT(self.game, None))
    except KeyError:
      # There can be unpredictable dependencies such that it's impossible
      # to ensure that this method is called only once. Ignore multiple calls
      pass

  def on_removal_event(self, sender, event):
    self.remove()

  def on_uninstall_card(self, sender, event):
    if self.card and sender == self.card:
      self.remove()


class IceStrengthModifier(Modifier):
  EVENT = events.IceStrengthChanged


class IceRezCostModifier(Modifier):
  pass


class RezCostModifier(Modifier):
  pass


class IcebreakerStrengthModifier(Modifier):
  pass


class ProgramStrengthModifier(Modifier):
  pass


class NumHqCardsToAccess(Modifier):
  pass


class NumRndCardsToAccess(Modifier):
  pass


class MemorySize(Modifier):
  pass


class RunnerMaxHandSize(Modifier):
  pass


class RunnerStartingHandSize(Modifier):
  pass


class CorpMaxHandSize(Modifier):
  pass


class CorpStartingHandSize(Modifier):
  pass


class StealAgendaCost(Modifier):
  pass


class AgendaAdvancementRequirement(Modifier):
  pass


class ProgramCostModifier(Modifier):
  pass


class HardwareCostModifier(Modifier):
  pass


class CardAccessRestriction(Modifier):
  """A modifier that restricts access to a single card (e.g. Ash).

  This is a pretty weird one since it's a non-numeric restriction, and
  has to be specially checked for by the accessed server. Weird on-offs
  are the way this works though I guess.
  """

  def __init__(self, game, value, until=None, server=None, card=None):
    Modifier.__init__(self, game, 0, until, server, card)
    self.access_card = value

