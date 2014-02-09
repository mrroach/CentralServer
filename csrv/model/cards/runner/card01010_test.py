import unittest
from csrv.model import cards
from csrv.model import deck
from csrv.model import events
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards import corp
from csrv.model.cards.runner import card01010


class Card01010Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01010.Card01010(self.game, self.game.runner)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))
    self.game.runner.grip.add(self.card)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))

    # Strength 1 barrier
    self.ice = cards.Registry.get('Card01103')(self.game, self.game.corp)
    self.ice.is_rezzed = True

  def test_install_card01010(self):
    self.assertIn(
        self.card.install_action, self.game.current_phase().choices())

  def test_card01010_gains_counter(self):
    self.game.runner.rig.add(self.card)
    self.skip_to_4_5()
    self.assertEqual(1, self.card.virus_counters)

  def test_card01010_provides_choice(self):
    self.game.runner.rig.add(self.card)
    self.card.virus_counters = 1
    self.skip_to_4_5()
    self.assertIsInstance(
        self.game.current_phase(), timing_phases.ChooseNumCardsToAccess)
    self.assertEqual(
        [self.card._choose_num_cards_action],
        self.game.current_phase().choices())
    response = self.card._choose_num_cards_action.request().new_response()
    response.number = 1
    self.game.resolve_current_phase(
        self.card._choose_num_cards_action, response)
    self.assertIsInstance(
        self.game.current_phase(), timing_phases.ApproachServer_4_5)
    self.assertEqual(2, self.game.corp.rnd.num_cards_to_access())

  def test_purge_virus_counters(self):
    self.game.runner.rig.add(self.card)
    self.card.virus_counters = 2
    self.game.trigger_event(
        events.PurgeVirusCounters(self.game, self.game.corp), None)
    self.assertEqual(0, self.card.virus_counters)

  def setup_run(self):
    run = self.game.new_run(self.game.corp.rnd)
    run.begin()

  def skip_to_4_5(self):
    self.setup_run()
    # Skip past phase 4.1
    self.game.current_phase().end_phase()
    # indicate that we want to continue the run
    self.game.resolve_current_phase(
        self.game.run._continue_run_action, None)
    # Skip past phase 4.3
    self.game.current_phase().end_phase()
    # Skip past phase 4.4
    self.game.current_phase().end_phase()
    self.game.current_phase().begin()


if __name__ == '__main__':
  unittest.main()
