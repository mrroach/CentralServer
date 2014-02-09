import unittest
from csrv.model import cards
from csrv.model import events
from csrv.model.cards import corp
from csrv.model import deck
from csrv.model import game
from csrv.model import modifiers
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.runner import card01012


class Card01012Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01012.Card01012(self.game, self.game.runner)
    self.game.runner.grip.add(self.card)
    self.runner.clicks.set(4)
    self.runner.credits.set(5)
    self.ice = cards.Registry.get('Card01113')(self.game, self.game.corp)
    self.ice.rez()
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))

  def test_no_install_card01012(self):
    self.assertNotIn(
        self.card.install_action, self.game.current_phase().choices())

  def test_install_card01012(self):
    self.game.corp.hq.install_ice(self.ice)
    self.assertIn(
        self.card.install_action, self.game.current_phase().choices())
    response = self.card.install_action.request().new_response()
    response.host = self.ice
    self.game.resolve_current_phase(
        self.card.install_action, response)
    self.assertEqual(3, self.ice.strength)
    self.game.trigger_event(
        events.RunnerTurnBegin(self.game, self.game.runner), self.game)
    self.assertEqual(2, self.ice.strength)
    self.game.trigger_event(
        events.RunnerTurnBegin(self.game, self.game.runner), self.game)
    self.assertEqual(1, self.ice.strength)
    self.game.trigger_event(
        events.RunnerTurnBegin(self.game, self.game.runner), self.game)
    self.assertEqual(self.game.corp.archives, self.ice.location)
    self.assertEqual(self.game.runner.heap, self.card.location)
    self.assertIsNone(self.card.host)

  def test_card01012_card01015_interaction(self):
    card01015 = [c for c in self.runner.stack.cards
                  if c.NAME == 'Card01015'][0]
    self.runner.stack.remove(card01015)
    self.runner.rig.add(card01015)
    self.runner.rig.add(self.card)
    self.corp.hq.install_ice(self.ice)
    self.ice.host_card(self.card)
    self.card.virus_counters = 2
    run = self.game.new_run(self.corp.hq)
    run.begin()
    self.game.current_phase().end_phase()  # skip 2.1
    self.game.current_phase().end_phase()  # skip 2.3
    self.game.current_phase().begin()
    # Check that the ice was trashed
    self.assertEqual(self.corp.archives, self.ice.location)
    self.assertIsNone(self.game.run.current_ice())
    self.assertIsInstance(
        self.game.current_phase(), timing_phases.ApproachServer_4_1)

  def test_card01012_card01008_interaction(self):
    other = [c for c in self.runner.stack.cards + self.runner.grip.cards
             if c.NAME == 'Card01008'][0]
    self.runner.rig.add(other)
    self.runner.rig.add(self.card)
    self.corp.hq.install_ice(self.ice)
    self.ice.host_card(self.card)
    self.card.virus_counters = 2
    other.virus_counters = 1
    run = self.game.new_run(self.corp.hq)
    run.begin()
    self.game.current_phase().end_phase()  # skip 2.1
    self.game.current_phase().end_phase()  # skip 2.3
    self.game.current_phase().begin()
    self.game.resolve_current_phase(
        other.interact_with_ice_actions()[0], None)
    self.assertEqual(self.corp.archives, self.ice.location)
    self.assertIsNone(self.game.run.current_ice())
    self.assertIsInstance(
        self.game.current_phase(), timing_phases.ApproachServer_4_1)

  def test_purge_virus_counters(self):
    self.corp.hq.install_ice(self.ice)
    self.ice.host_card(self.card)
    self.runner.rig.add(self.card)
    self.card.virus_counters = 2
    self.game.trigger_event(
        events.PurgeVirusCounters(self.game, self.corp), None)
    self.assertEqual(0, self.card.virus_counters)


if __name__ == '__main__':
  unittest.main()
