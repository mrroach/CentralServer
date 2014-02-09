import unittest
from csrv.model import cards
from csrv.model.cards import corp
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.runner import card01020


class Card01020Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01020.Card01020(self.game, self.game.runner)
    self.corp.credits.set(5)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.runner.grip.add(self.card)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))
    self.ice = cards.Registry.get('Card01103')(self.game, self.corp)
    self.corp.rnd.install_ice(self.ice)

  def test_forced_rez(self):
    self.assertIn(
        self.card._play_event_action, self.game.current_phase().choices())
    self.game.resolve_current_phase(self.card._play_event_action, None)
    self.assertIsInstance(self.game.current_phase(),
                          card01020.ChooseUnrezzedIce)
    choices = self.game.current_phase().choices()
    self.assertEqual(1, len(choices))
    self.game.resolve_current_phase(choices[0], None)
    self.assertIsInstance(self.game.current_phase(),
                          card01020.RezOrTrash)
    choices = self.game.current_phase().choices()
    self.assertEqual(1, len(choices))
    self.assertEqual(self.ice, choices[0].card)
    self.assertEqual(6, self.corp.credits.value)  # +1 from installing
    self.game.resolve_current_phase(choices[0], None)
    self.assertTrue(self.ice.is_rezzed)
    self.assertEqual(5, self.corp.credits.value)

  def test_forced_trash(self):
    self.assertIn(
        self.card._play_event_action, self.game.current_phase().choices())
    self.game.resolve_current_phase(self.card._play_event_action, None)
    self.assertIsInstance(self.game.current_phase(),
                          card01020.ChooseUnrezzedIce)
    choices = self.game.current_phase().choices()
    self.assertEqual(1, len(choices))
    self.game.resolve_current_phase(choices[0], None)
    self.assertIsInstance(self.game.current_phase(),
                          card01020.RezOrTrash)
    choices = self.game.current_phase().choices()
    self.assertEqual(1, len(choices))
    self.assertEqual(self.ice, choices[0].card)
    self.assertEqual(6, self.corp.credits.value)  # +1 from installing
    self.game.resolve_current_phase(None, None)
    self.assertEqual(self.corp.archives, self.ice.location)
    self.assertEqual(6, self.corp.credits.value)


if __name__ == '__main__':
  unittest.main()
