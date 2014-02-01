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
    for name in card_names:
      c = cards.Registry.get(name)
      if c:
        self.cards.append(c)


class CorpDeck(Deck):
  """A deck for a corp."""

  def validate(self):
    """Return a list of errors with the deck."""
    return []


class RunnerDeck(Deck):
  """A deck for a runner."""

  def validate(self):
    """Return a list of errors with the deck."""
    return []

