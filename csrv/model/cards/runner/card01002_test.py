import unittest
from csrv.model import cards
from csrv.model.cards import corp
from csrv.model.cards import runner
from csrv.model import deck
from csrv.model import errors
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.runner import card01002


class TestCard01002(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01002.Card01002(self.game, self.game.runner)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.runner.grip.add(self.card)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))

  def test_unusable_with_empty_heap(self):
    self.assertNotIn(
        self.card._play_event_action, self.game.current_phase().choices())

  def test_usable_with_cards_in_heap(self):
    for card in self.game.runner.stack.cards[-2:]:
      card.trash()
    self.assertIn(
        self.card._play_event_action, self.game.current_phase().choices())

  def test_can_retrieve_one_card(self):
    card = self.game.runner.stack.cards[-1]
    card.trash()
    response = self.card._play_event_action.request().new_response()
    response.cards.append(card)
    self.game.resolve_current_phase(self.card._play_event_action, response)
    self.assertIn(card, self.game.runner.grip.cards)
    self.assertEqual(3, self.game.runner.credits.value)

  def test_can_retrieve_two_cards(self):
    cards = [c for c in self.runner.stack.cards if c.NAME == 'Card01010']
    [c.trash() for c in cards]
    response = self.card._play_event_action.request().new_response()
    response.cards.extend(cards)
    self.game.resolve_current_phase(self.card._play_event_action, response)
    self.assertIn(cards[0], self.game.runner.grip.cards)
    self.assertIn(cards[1], self.game.runner.grip.cards)

  def test_can_not_retrieve_two_non_viruses(self):
    cards = []
    for card in self.runner.stack.cards:
      if card.NAME == 'Card01010':
        cards.append(card)
        card.trash()
        break
    for card in self.runner.stack.cards:
      if card.NAME == 'Card01005':
        cards.append(card)
        card.trash()
        break
    self.assertEqual(2, len(cards))
    response = self.card._play_event_action.request().new_response()
    response.cards.extend(cards)
    self.assertRaises(
        errors.InvalidResponse, self.game.resolve_current_phase,
        self.card._play_event_action, response)
    self.assertIn(cards[0], self.game.runner.heap.cards)
    self.assertIn(cards[1], self.game.runner.heap.cards)


if __name__ == '__main__':
  unittest.main()
