import unittest
from csrv.model import actions
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards.runner import card01030


class TestCard01030(test_base.TestBase):
  RUNNER_DECK = 'Shaper Core'

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01030.Card01030(self.game, self.game.runner)

  def test_prevent_damage(self):
    self.runner.rig.add(self.card)
    self.game.insert_next_phase(
        timing_phases.TakeMeatDamage(self.game, self.runner, 4))
    self.assertIn(self.card._prevent_meat_damage,
                  self.game.current_phase().choices())
    self.game.resolve_current_phase(self.card._prevent_meat_damage, None)
    self.assertEqual(self.runner.heap, self.card.location)
    self.assertEqual(1, self.game.current_phase().damage)

  def test_remove_tags(self):
    self.runner.rig.add(self.card)
    self.runner.tags = 1
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.runner))
    self.runner.credits.set(0)
    self.runner.clicks.set(1)
    remove_tag = actions.RemoveATag(self.game, self.runner)
    self.assertTrue(remove_tag.is_usable())
    self.game.resolve_current_phase(remove_tag, None)
    self.assertEqual(0, self.runner.tags)
    self.assertEqual(0, self.card.pool.value)


if __name__ == '__main__':
  unittest.main()
