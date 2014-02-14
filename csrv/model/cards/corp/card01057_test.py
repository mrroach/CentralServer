import unittest
from csrv.model import errors
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.corp import card01057


class Card01057Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01057.Card01057(self.game, self.corp)
    self.corp.clicks.set(3)
    self.corp.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.CorpTurnActions(self.game, self.corp))

    # Add some programs to the rig
    for name in ['Card01007', 'Card01010', 'Card01051', 'Card01014']:
      for c in list(self.runner.stack.cards):
        if c.NAME == name:
          self.runner.stack.remove(c)
          self.runner.rig.add(c)
          break

  def test_access_advanced_ambush(self):
    server = self.corp.new_remote_server()
    server.install(self.card)
    self.card.advance()
    self.card.advance()
    run = self.game.new_run(server)
    run.begin()
    self.game.current_phase().end_phase()  # end phase 4.1
    self.game.resolve_current_phase(run._continue_run_action, None)  # 4.2
    self.game.current_phase().end_phase()  # end phase 4.3
    self.game.current_phase().end_phase()  # end phase 4.4
    access = self.game.current_phase().choices()[0]
    self.game.resolve_current_phase(access, None)  # choose to access
    self.assertTrue(self.game.current_phase().begun)
    yes_action = self.game.current_phase().yes_action
    self.game.resolve_current_phase(yes_action, None)

    # one choice per installed program
    choices = self.game.current_phase().choices()
    self.assertEqual(4, len(choices))
    self.game.resolve_current_phase(choices[0], None)
    self.assertEqual(4, len(choices))
    self.game.resolve_current_phase(choices[1], None)
    self.assertIsInstance(
        self.game.current_phase(), timing_phases.TrashAProgram)
    self.game.resolve_current_phase(None, None)
    self.assertIsInstance(
        self.game.current_phase(), timing_phases.TrashAProgram)
    self.game.resolve_current_phase(None, None)
    self.assertEqual(2, self.runner.heap.size)
    self.assertEqual(2, self.runner.rig.size)
    self.assertEqual(4, self.corp.credits.value)


if __name__ == '__main__':
  unittest.main()
