import unittest
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards.runner import card01045


class TestCard01045(test_base.TestBase):
  RUNNER_DECK = 'Shaper Core'

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01045.Card01045(self.game, self.game.runner)
    self.game.runner.grip.add(self.card)

  def test_prevent_damage(self):
    self.game.runner.credits.set(4)
    self.game.runner.rig.add(self.card)
    self.game.insert_next_phase(
        timing_phases.TakeNetDamage(self.game, self.runner, 2))
    self.assertIn(self.card._prevent_net_damage,
                  self.game.current_phase().choices())
    self.game.resolve_current_phase(self.card._prevent_net_damage, None)
    self.assertEqual(1, self.game.current_phase().damage)
    self.assertEqual(0, len(self.game.current_phase().choices()))


if __name__ == '__main__':
  unittest.main()
