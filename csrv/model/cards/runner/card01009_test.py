import unittest
from csrv.model import cards
from csrv.model.cards import corp
from csrv.model import errors
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.runner import card01009


class Card01009Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01009.Card01009(self.game, self.game.runner)
    for c in self.runner.grip.cards:
      self.runner.stack.add(c)
    self.viruses = [c for c in self.runner.stack.cards
                    if c.NAME in ['Card01010', 'Card01008']]
    self.virus = self.viruses[0]
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))
    self.game.runner.grip.add(self.card)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))

  def test_install_card01009(self):
    self.assertIn(
        self.card.install_action, self.game.current_phase().choices())

  def test_retrieve_virus(self):
    self.game.runner.rig.add(self.card)
    self.assertIn(
        self.card._retrieve_virus_action, self.game.current_phase().choices())
    response = self.card._retrieve_virus_action.request().new_response()
    response.card = self.virus
    self.game.resolve_current_phase(
        self.card._retrieve_virus_action, response)
    self.assertEqual(4, self.game.runner.credits.value)
    self.assertEqual(3, self.game.runner.clicks.value)
    self.assertIn(response.card, self.game.runner.grip.cards)

  def test_host_program(self):
    self.game.runner.rig.add(self.card)
    response = self.virus.install_action.request().new_response()
    response.host = self.card
    self.game.resolve_current_phase(self.virus.install_action, response)
    self.assertEqual(3, self.game.runner.free_memory)

  def test_memory_limits(self):
    self.game.runner.rig.add(self.card)
    self.assertEqual(3, len(self.viruses[1:]))
    for card in self.viruses[1:]:
      self.game.runner.rig.add(card)
      self.card.host_card(card)
    self.assertEqual(3, self.game.runner.free_memory)
    response = self.virus.install_action.request().new_response()
    response.host = self.card
    self.assertRaises(
        errors.InvalidResponse,
        self.game.resolve_current_phase, self.virus.install_action, response)
    to_trash = list(self.card.hosted_cards)[0]
    response.programs_to_trash.append(to_trash)
    self.game.resolve_current_phase(self.virus.install_action, response)
    self.assertEqual(self.game.runner.heap, to_trash.location)


if __name__ == '__main__':
  unittest.main()
