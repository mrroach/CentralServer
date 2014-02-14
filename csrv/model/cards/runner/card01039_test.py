import unittest
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.runner import card01039


class TestCard01039(test_base.TestBase):
  RUNNER_DECK = 'Shaper Core'

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01039.Card01039(self.game, self.game.runner)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))
    self.game.runner.grip.add(self.card)

  def test_recursive_install(self):
    # verify that card is installable
    self.assertIn(
        self.card.install_action, self.game.current_phase().choices())
    self.game.resolve_current_phase(self.card.install_action, None)

    # verify cost charged (no discount since turn didn't begin)
    self.assertEqual(3, self.game.runner.credits.value)

    # verify card is installed
    self.assertIn(self.card, self.game.runner.rig.cards)
    self.assertTrue(self.card.is_installed)
    self.assertIsInstance(self.game.current_phase(),
                          card01039.DecideInstallOther)
    phase = self.game.current_phase()
    self.game.resolve_current_phase(phase.yes_action, None)
    self.assertEqual(1, self.game.runner.credits.value)


if __name__ == '__main__':
  unittest.main()
