import unittest
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.runner import card01053


class TestCard01053(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01053.Card01053(
        self.game, self.game.runner)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))
    self.game.runner.grip.add(self.card)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))

  def test_gain_money(self):
    # verify that card is installable
    self.assertIn(
        self.card.install_action, self.game.current_phase().choices())
    self.game.resolve_current_phase(self.card.install_action, None)

    # verify cost charged
    self.assertEqual(4, self.game.runner.credits.value)

    # verify card is installed
    self.assertIn(self.card, self.game.runner.rig.cards)
    self.assertTrue(self.card.is_installed)

    # resolve abilities
    self.game.resolve_current_phase(None, None)
    self.game.resolve_current_phase(None, None)

    # verify that credit gain ability is available
    self.assertIn(
        self.card._gain_credits_ability, self.game.current_phase().choices())

    # verify that the gain credit ability works
    self.game.resolve_current_phase(self.card._gain_credits_ability, None)
    self.assertEqual(6, self.game.runner.credits.value)

    # fast forward to an almost-empty card
    self.card.pool.set(2)

    # resolve abilities
    self.game.resolve_current_phase(None, None)
    self.game.resolve_current_phase(None, None)

    # verify that the card self-trashes when empty
    self.game.resolve_current_phase(self.card._gain_credits_ability, None)
    self.assertFalse(self.card.is_installed)
    self.assertNotIn(self.card, self.game.runner.rig.cards)


if __name__ == '__main__':
  unittest.main()
