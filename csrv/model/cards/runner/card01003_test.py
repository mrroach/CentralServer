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
from csrv.model.cards.runner import card01003


class Card01003Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01003.Card01003(self.game, self.game.runner)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.runner.grip.add(self.card)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))

  def test_playable(self):
    self.assertIn(self.card._play_event_action,
        self.game.current_phase().choices())

  def test_trash_asset(self):
    card = cards.Registry.get('Card01108')(self.game, self.game.corp)
    server = self.game.corp.new_remote_server()
    server.install(card)
    response = self.card._play_event_action.request().new_response()
    response.server = server
    self.game.resolve_current_phase(self.card._play_event_action, response)

    choice = [c for c in self.game.current_phase().choices()
              if c.server == server][0]
    self.game.resolve_current_phase(choice, None)

    # Skip past phase 4_1
    self.game.current_phase().end_phase()

    # indicate that we want to continue the run
    self.game.resolve_current_phase(
        self.game.run._continue_run_action, None)

    # Skip past phase 4_3
    self.game.current_phase().end_phase()

    # Skip past phase 4_4
    self.game.current_phase().end_phase()

    self.assertEqual(1, len(self.game.current_phase().choices()))
    self.game.resolve_current_phase(
        self.game.current_phase().choices()[0], None)
    trash_for_free = [c for c in self.game.current_phase().choices()
                      if isinstance(c, card01003.TrashForFree)]
    self.assertEqual(1, len(trash_for_free))
    self.game.resolve_current_phase(trash_for_free[0], None)
    self.assertEqual(self.game.corp.archives, card.location)
    self.assertEqual(3, self.game.runner.credits.value)


if __name__ == '__main__':
  unittest.main()
