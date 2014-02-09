import unittest
from csrv.model import cards
from csrv.model.cards import corp
from csrv.model.cards import runner
from csrv.model import deck
from csrv.model import errors
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.runner import card01004


class Card01004Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01004.Card01004(self.game, self.game.runner)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.runner.grip.add(self.card)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))

  def test_playable(self):
    self.assertIn(self.card._play_event_action,
        self.game.current_phase().choices())

  def test_card(self):
    card = cards.Registry.get('Card01108')(self.game, self.game.corp)
    server = self.game.corp.new_remote_server()
    server.install(card)
    response = self.card._play_event_action.request().new_response()
    response.server = server
    self.game.resolve_current_phase(self.card._play_event_action, response)

    self.assertEqual(1, len(self.game.runner.credit_pools))
    self.assertEqual(9, list(self.game.runner.credit_pools)[0].value)

    choice = [c for c in self.game.current_phase().choices()
              if c.server == server][0]
    self.game.resolve_current_phase(choice, None)

    self.assertEqual(2, len(self.game.runner.find_pools()))
    self.assertEqual(
        14, sum([p.value for p in self.game.runner.find_pools()]))

    # Skip past phase 4_1
    self.game.current_phase().end_phase()

    # indicate that we want to continue the run
    self.game.resolve_current_phase(
        self.game.run._jack_out_action, None)
    self.assertIsInstance(
        self.game.current_phase(), timing_phases.TakeBrainDamage)
    choices = self.game.current_phase().choices()
    self.assertEqual(0, len(choices))
    self.game.resolve_current_phase(None, None)
    self.assertTrue(self.game.runner_flatlined)
    self.assertTrue(self.game.corp_wins)
    self.assertEqual(4, self.game.runner.max_hand_size)
    self.assertEqual(1, self.game.runner.brain_damage)


if __name__ == '__main__':
  unittest.main()
