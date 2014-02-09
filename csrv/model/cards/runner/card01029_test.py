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
from csrv.model.cards.runner import card01029


class Card01029Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01029.Card01029(self.game, self.game.runner)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.runner.grip.add(self.card)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))

  def test_installable(self):
    self.assertIn(self.card.install_action,
        self.game.current_phase().choices())

  def test_take_money(self):
    card = cards.Registry.get('Card01108')(self.game, self.game.corp)
    server = self.game.corp.new_remote_server()
    server.install(card)
    self.game.resolve_current_phase(self.card.install_action, None)
    self.game.new_run(server)
    self.game.run.begin()

    # Skip past phase 4_1
    self.game.current_phase().end_phase()

    # indicate that we want to continue the run
    self.game.resolve_current_phase(
        self.game.run._continue_run_action, None)

    # Skip past phase 4_3
    self.game.current_phase().end_phase()

    # end phase 4_4
    self.game.current_phase().end_phase()

    # Instead of phase 4.5, we should have a choice of access phases
    self.assertIsInstance(self.game.current_phase(),
        timing_phases.SelectAccessPhase)

    # Choose the access phase corresponding to our card
    for choice in self.game.current_phase().choices():
      if choice.card == self.card:
        self.game.resolve_current_phase(choice, None)
        break
    else:
      self.fail()

    # There should be only one choice now: how much money to take
    choices = self.game.current_phase().choices()
    self.assertEqual(1, len(choices))
    response = choices[0].request().new_response()
    response.number = 8
    self.game.resolve_current_phase(choices[0], response)

    # Bank Job should have 0 credits and be in the trash
    self.assertEqual(0, self.card.credits)
    self.assertEqual(self.game.runner.heap, self.card.location)


if __name__ == '__main__':
  unittest.main()
