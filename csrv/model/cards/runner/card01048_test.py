import unittest
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards.runner import card01048


class TestCard01048(test_base.TestBase):
  RUNNER_DECK = 'Maker Core'

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01048.Card01048(self.game, self.game.runner)
    self.game.runner.grip.add(self.card)

  def test_prevent_trash(self):
    self.game.runner.rig.add(self.card)
    for card in self.runner.stack.cards:
      if card.TYPE == card_info.PROGRAM:
        program = card
        self.runner.rig.add(program)
        break
    self.game.insert_next_phase(
        timing_phases.TrashAProgram(self.game, self.runner, program))
    self.assertIn(self.card._prevent_trash, self.game.current_phase().choices())
    self.game.resolve_current_phase(self.card._prevent_trash, None)
    self.assertEqual(self.runner.heap, self.card.location)


if __name__ == '__main__':
  unittest.main()
