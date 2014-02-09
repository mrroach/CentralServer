import unittest
from csrv.model import cards
from csrv.model.cards import corp
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.runner import card01005


class Card01005Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01005.Card01005(self.game, self.game.runner)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.runner.grip.add(self.card)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))

  def test_install_card01005(self):
    self.assertIn(
        self.card.install_action, self.game.current_phase().choices())
    self.game.resolve_current_phase(self.card.install_action, None)
    self.assertEqual(3, self.game.runner.credits.value)
    self.assertEqual(1, len(self.game.runner.credit_pools))
    self.assertEqual(1, list(self.game.runner.credit_pools)[0].value)
    self.card.trash()
    self.assertEqual(0, len(self.game.runner.credit_pools))


if __name__ == '__main__':
  unittest.main()
