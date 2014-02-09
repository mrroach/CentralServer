import unittest
from csrv.model import cards
from csrv.model.cards import corp
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.runner import card01015


class Card01015Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01015.Card01015(self.game, self.game.runner)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))
    self.game.runner.grip.add(self.card)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))

    self.ice = cards.Registry.get('Card01103')(self.game, self.game.corp)
    self.ice.is_rezzed = True

  def test_install_card01015(self):
    self.assertIn(
        self.card.install_action, self.game.current_phase().choices())

  def test_card01015_lowers_strength(self):
    self.setup_run()
    self.game.runner.rig.add(self.card)
    # push the begin button directly since we got here through weird channels
    self.game.current_phase().begin()
    self.assertEqual(0, self.ice.strength)

  def setup_run(self):
    server = self.game.corp.new_remote_server()
    server.install_ice(self.ice)
    self.game.new_run(server)
    self.game.run.encounter_ice()
    self.assertEqual(self.ice, self.game.run.current_ice())


if __name__ == '__main__':
  unittest.main()
