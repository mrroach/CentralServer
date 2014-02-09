import unittest
from csrv.model import cards
from csrv.model.cards import corp
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.runner import card01006


class Card01006Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01006.Card01006(self.game, self.game.runner)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.runner.grip.add(self.card)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))

  def tearDown(self):
    self.card.trash()

  def test_install_card01006(self):
    self.assertIn(
        self.card.install_action, self.game.current_phase().choices())
    self.game.resolve_current_phase(self.card.install_action, None)
    self.assertEqual(6, self.game.runner.free_memory)

  def test_card01006_adds_virus_counter(self):
    self.game.runner.rig.add(self.card)
    virus = [c for c in self.runner.stack.cards if c.NAME == 'Card01008'][0]
    self.game.runner.rig.add(virus)
    self.assertEqual(1, virus.virus_counters)


if __name__ == '__main__':
  unittest.main()
