import unittest
from csrv.model import cards
from csrv.model import errors
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.corp import card01100


class Card01100Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01100.Card01100(self.game, self.corp)
    self.corp.clicks.set(3)
    self.corp.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.CorpTurnActions(self.game, self.corp))
    self.agenda = cards.Registry.get('Card01055')(self.game, self.corp)
    self.ice = cards.Registry.get('Card01103')(self.game, self.corp)
    self.corp.hq.add(self.card)

  def test_advance_two_things(self):
    server = self.corp.new_remote_server()
    server.install(self.agenda)
    server.install_ice(self.ice)
    self.assertIn(
        self.card._play_operation_action,
        self.game.current_phase().choices())
    self.game.resolve_current_phase(self.card._play_operation_action, None)

    self.assertIsInstance(self.game.current_phase(),
                          card01100.ChooseCardsToAdvance)
    choices = self.game.current_phase().choices()
    self.assertEqual(2, len(choices))
    self.game.resolve_current_phase(choices[0], None)
    self.assertEqual(1, choices[0].card.advancement_tokens)

    self.assertIsInstance(self.game.current_phase(),
                          card01100.ChooseCardsToAdvance)
    choices = self.game.current_phase().choices()
    self.assertEqual(1, len(choices))
    self.game.resolve_current_phase(choices[0], None)
    self.assertEqual(1, choices[0].card.advancement_tokens)

    self.assertIsInstance(self.game.current_phase(),
                          timing_phases.CorpTurnAbilities)


if __name__ == '__main__':
  unittest.main()
