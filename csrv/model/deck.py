"""A collection of cards."""

import random
from csrv.model import cards
from csrv.model.cards import card_info

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

  def _verify_less_than_three_copies(self):
    """Make sure we have no more than 3 copies of a single cards"""
    card_list = {}
    for c in self.cards:
      card_list[c.NAME] = card_list.setdefault(c.NAME, 0) + 1

    invalid_cards = filter(lambda x: card_list[x] > 3, card_list)
    if len(invalid_cards):
      return "Deck contains more than 3 copies of the following cards: {}".format(', '.join(invalid_cards))

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

  def _verify_side_only(self, side):
    """Make sure we only have cards belonging to the correct side"""
    if len(filter(lambda c: c.SIDE != side, self.cards)):
      return "Deck contains cards from the other side (corp/runner)"

class CorpDeck(Deck):
  """A deck for a corp."""

  def validate(self):
    """Return a list of errors with the deck."""
    return filter(None, [
      self._verify_min_deck_size(),
      self._verify_influence_points(),
      self._verify_less_than_three_copies(),
      self._verify_in_faction_agendas(),
      self._verify_agenda_points(),
      self._verify_side_only(card_info.CORP)
    ])

  def _verify_agenda_points(self):
    """Make sure deck has required agenda points based on deck size"""
    agenda_points = reduce(lambda x,y: x+y.AGENDA_POINTS, self.cards, 0)
    deck_size = len(self.cards)
    if agenda_points/float(deck_size) < 2.0/5.0:
      self.is_valid = False
      return "Only {} Agenda Points in deck of {} cards".format(agenda_points, deck_size)

  def _verify_in_faction_agendas(self):
    """Make sure deck only contains in faction agendas"""
    agendas = filter(lambda c: c.TYPE == card_info.AGENDA, self.cards)

    if len(filter(lambda a: not a.FACTION in [card_info.NEUTRAL, self.identity.FACTION], agendas)):
      return "Deck contains out-of-faction Agendas"

class RunnerDeck(Deck):
  """A deck for a runner."""

  def validate(self):
    """Return a list of errors with the deck."""
    return filter(None, [
      self._verify_min_deck_size(),
      self._verify_influence_points(),
      self._verify_less_than_three_copies(),
      self._verify_side_only(card_info.RUNNER)
    ])

