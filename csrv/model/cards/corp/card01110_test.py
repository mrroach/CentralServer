import unittest
from csrv.model import errors
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.corp import card01110


class HedgeFundTest(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01110.Card01110(self.game, self.corp)
    self.corp.clicks.set(3)
    self.corp.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.CorpTurnActions(self.game, self.corp))

  def test_play(self):
    self.corp.hq.add(self.card)
    self.assertIn(
        self.card._play_operation_action, self.game.current_phase().choices())
    self.game.resolve_current_phase(
        self.card._play_operation_action, None)
    self.assertEqual(9, self.corp.credits.value)


if __name__ == '__main__':
  unittest.main()
