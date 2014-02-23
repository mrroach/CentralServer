import unittest
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards.runner import card01032


class TestCard01032(test_base.TestBase):
  RUNNER_DECK = 'Maker Core'

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01032.Card01032(self.game, self.game.runner)
    self.game.runner.grip.add(self.card)

  def test_prevent_tag(self):
    self.game.runner.rig.add(self.card)
    self.game.insert_next_phase(
        timing_phases.TakeTags(self.game, self.runner, 2))
    self.assertIn(self.card._prevent_a_tag, self.game.current_phase().choices())
    self.game.resolve_current_phase(self.card._prevent_a_tag, None)
    self.assertEqual(self.runner.heap, self.card.location)
    self.game.resolve_current_phase(None, None)
    self.assertEqual(1, self.runner.tags)


if __name__ == '__main__':
  unittest.main()
