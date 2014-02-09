import unittest
from csrv.model import cards
from csrv.model.cards import corp
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.runner import card01016


class Card01016Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01016.Card01016(self.game, self.game.runner)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.runner.grip.add(self.card)

  def test_install_card01016(self):
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))
    self.assertIn(
        self.card.install_action, self.game.current_phase().choices())

  def test_card01016_is_mandatory(self):
    self.game.runner.clicks.set(0)
    self.game.runner.rig.add(self.card)
    del self.game.timing_phases[:]
    self.game._add_runner_turn_phases()
    self.game.current_phase().end_phase()
    self.game.current_phase().begin()
    self.assertTrue(self.game.current_phase().choices()[0].is_mandatory)
    self.game.resolve_current_phase(None, None)
    self.game.resolve_current_phase(self.card._card01016_action, None)
    self.assertEqual(3, self.game.runner.clicks.value)
    self.assertEqual(2, self.game.runner.grip.size)

  def test_trashable_by_corp_when_tagged(self):
    self.game.runner.tags += 1
    self.game.runner.rig.add(self.card)
    self.game.corp.clicks.set(3)
    self.game.corp.credits.set(5)
    del self.game.timing_phases[:]
    self.game.insert_next_phase(
        timing_phases.CorpTurnActions(self.game, self.game.corp))
    choices = self.game.current_phase().choices()
    trash_choices = [c for c in choices if c.card == self.card]
    self.assertEqual(1, len(trash_choices))
    self.game.resolve_current_phase(trash_choices[0], None)
    self.assertEqual(2, self.game.corp.clicks.value)
    self.assertEqual(3, self.game.corp.credits.value)
    self.assertEqual(self.game.runner.heap, self.card.location)


if __name__ == '__main__':
  unittest.main()
