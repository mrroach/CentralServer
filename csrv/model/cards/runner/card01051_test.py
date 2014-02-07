import unittest
from csrv.model.actions import ai_break_subroutine
from csrv.model import cards
from csrv.model.cards import corp
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import timing_phases
from csrv.model.cards.runner import card01051


class TestCard01051(unittest.TestCase):

  def setUp(self):
    self.corp_deck = deck.CorpDeck(
        premade_decks.corp_decks[0]['identity'],
        premade_decks.corp_decks[0]['cards'])
    self.runner_deck = deck.RunnerDeck(
        premade_decks.runner_decks[0]['identity'],
        premade_decks.runner_decks[0]['cards'])
    self.game = game.Game(self.corp_deck, self.runner_deck)
    self.card = card01051.Card01051(self.game, self.game.runner)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))
    self.game.runner.grip.add(self.card)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))

    self.ice = cards.Registry.get('Card01103')(self.game, self.game.corp)
    self.ice.is_rezzed = True

  def test_install_card(self):
    self.assertIn(
        self.card.install_action, self.game.current_phase().choices())

  def test_charge_card(self):
    self.game.runner.rig.add(self.card)
    self.assertIn(
        self.card._place_virus_counter, self.game.current_phase().choices())
    self.game.resolve_current_phase(self.card._place_virus_counter, None)
    self.assertEqual(1, self.card.virus_counters)

  def test_break_and_trash_card(self):
    self.setup_run()
    self.game.runner.rig.add(self.card)
    self.assertIn(self.card._boost_strength_action,
                  self.game.current_phase().choices())
    self.game.resolve_current_phase(
        self.card._boost_strength_action, None)
    self.assertEqual(1, self.card.strength)
    self.assertEqual(4, self.game.runner.credits.value)
    break_action = [
        a for a in self.game.current_phase().choices()
        if isinstance(a, ai_break_subroutine.AiBreakSubroutine)]
    self.assertEqual(1, len(break_action))
    self.game.resolve_current_phase(break_action[0], None)
    self.assertTrue(self.ice.subroutines[0].is_broken)

    # Get past 3.1 and 3.2
    self.game.resolve_current_phase(None, None)
    self.game.resolve_current_phase(None, None)
    self.game.resolve_current_phase(None, None)

    # Check the the card trashed itself.
    self.assertEqual(self.game.runner.heap, self.card.location)

  def test_break_and_lose_counter(self):
    self.setup_run()
    self.card.virus_counters += 1
    self.game.runner.rig.add(self.card)
    self.assertIn(self.card._boost_strength_action,
                  self.game.current_phase().choices())
    self.game.resolve_current_phase(
        self.card._boost_strength_action, None)
    self.assertEqual(1, self.card.strength)
    self.assertEqual(4, self.game.runner.credits.value)
    break_action = [
        a for a in self.game.current_phase().choices()
        if isinstance(a, ai_break_subroutine.AiBreakSubroutine)]
    self.assertEqual(1, len(break_action))
    self.game.resolve_current_phase(break_action[0], None)
    self.assertTrue(self.ice.subroutines[0].is_broken)

    # Get past 3.1 and 3.2
    self.game.resolve_current_phase(None, None)
    self.game.resolve_current_phase(None, None)
    self.game.resolve_current_phase(None, None)

    # Check the the card loses a counter.
    self.assertEqual(self.game.runner.rig, self.card.location)
    self.assertEqual(0, self.card.virus_counters)

  def setup_run(self):
    server = self.game.corp.new_remote_server()
    server.install_ice(self.ice)
    self.game.new_run(server)
    self.game.run.encounter_ice()
    self.assertEqual(self.ice, self.game.run.current_ice())



if __name__ == '__main__':
  unittest.main()
