"""A collection of cards."""

import random
from csrv.model import cards

# This import is just to pull in all the card definitions
import csrv.model.cards.corp
import csrv.model.cards.runner


class Deck(object):

  def __init__(self, identity_name, card_names):
    self.identity = cards.Registry.get(identity_name)
    self.cards = []
    self.is_valid = True
    for name in card_names:
      c = cards.Registry.get(name)
      if c:
        self.cards.append(c)

  def _verify_min_deck_size(self):
    """Make sure deck meets minimum deck size limit"""
    if len(self.cards) < self.identity.MIN_DECK_SIZE:
      self.is_valid = False
      return "Deck does not meet minimum deck size requirement"

  def _verify_influence_points(self):
    """Make sure deck doesnt exceed maximum influence points"""
    influence_spent = reduce(lambda x,y: x+y.influence_cost(self.identity.FACTION), self.cards, 0)
    if influence_spent > self.identity.MAX_INFLUENCE:
      return "Deck contains {} influence but only {} allowed".format(influence_spent, self.identity.MAX_INFLUENCE)

class CorpDeck(Deck):
  """A deck for a corp."""

  def validate(self):
    """Return a list of errors with the deck."""
    return filter(None, [
      self._verify_min_deck_size(),
      self._verify_influence_points(),
      self._verify_agenda_points()
    ])

  def _verify_agenda_points(self):
    """Make sure deck has required agenda points based on deck size"""
    agenda_points = reduce(lambda x,y: x+y.AGENDA_POINTS, self.cards, 0)
    deck_size = len(self.cards)
    if agenda_points/float(deck_size) < 2.0/5.0:
      self.is_valid = False
      return "Only {} Agenda Points in deck of {} cards".format(agenda_points, deck_size)

class RunnerDeck(Deck):
  """A deck for a runner."""

  def validate(self):
    """Return a list of errors with the deck."""
    return filter(None, [
      self._verify_min_deck_size(),
      self._verify_influence_points()
    ])

