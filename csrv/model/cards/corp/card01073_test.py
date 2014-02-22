import unittest
from csrv.model import errors
from csrv.model import events
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.corp import card01073


class Card01073Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01073.Card01073(self.game, self.corp)
    self.corp.clicks.set(3)
    self.corp.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.CorpTurnActions(self.game, self.corp))
    self.corp.hq.add(self.card)

  def test_rearrange_cards(self):
    choices = self.game.current_phase().choices()
    self.assertIn(self.card._play_operation_action, choices)
    self.game.resolve_current_phase(self.card._play_operation_action, None)
    self.assertIsInstance(self.game.current_phase(),
                          card01073.RearrangeCardsPhase)
    self.assertEqual(1, len(self.game.current_phase().choices()))
    choices = self.game.current_phase().choices()
    request = choices[0].request()
    cards = request.cards
    new_order = [cards[3], cards[1], cards[2], cards[0], cards[4]]
    response = request.new_response()
    response.cards = new_order
    self.game.resolve_current_phase(choices[0], response)
    self.assertEqual(list(reversed(new_order)), self.corp.rnd.cards[-5:])


if __name__ == '__main__':
  unittest.main()
