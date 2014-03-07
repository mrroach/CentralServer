import unittest
from csrv.model import cards
from csrv.model.cards import corp
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.runner import card01023


class Card01023Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01023.Card01023(self.game, self.game.runner)
    self.corp.credits.set(5)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.runner.grip.add(self.card)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))
    self.ice = cards.Registry.get('Card01103')(self.game, self.corp)
    self.corp.rnd.install_ice(self.ice)

  def test_unusable_without_run(self):
    self.runner.rig.add(self.card)
    self.assertNotIn(
        self.card._expose_action,
        self.game.current_phase().choices())

  def test_usable_with_run(self):
    self.runner.rig.add(self.card)
    run = self.game.new_run(self.corp.hq)
    run.successful_run()
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))
    self.assertIn(
        self.card._expose_action,
        self.game.current_phase().choices())
    response = self.card._expose_action.request().new_response()
    response.card = self.ice
    self.game.resolve_current_phase(self.card._expose_action, response)
    self.assertIn(self.ice.game_id, self.game.exposed_ids)


if __name__ == '__main__':
  unittest.main()
