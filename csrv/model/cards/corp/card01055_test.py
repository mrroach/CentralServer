import unittest
from csrv.model import errors
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.corp import card01055


class Card01055Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01055.Card01055(
        self.game, self.corp)
    self.corp.clicks.set(3)
    self.corp.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.CorpTurnActions(self.game, self.corp))

    # Put everything back in R&D to avoid test flakiness
    for card in list(self.corp.hq.cards):
      self.corp.hq.remove(card)
      self.corp.rnd.add(card)

    # Sort R&D to have 2 ice and one operation on top
    for card in list(self.corp.rnd.cards):
      if card.NAME == 'Card01113':
        self.corp.rnd.remove(card)
        self.corp.rnd.add(card)

    for card in list(self.corp.rnd.cards):
      if card.NAME == 'Card01110':
        self.corp.rnd.remove(card)
        self.corp.rnd.add(card)
        break  # only one copy

  def install_and_score(self):
    server = self.corp.new_remote_server()
    server.install(self.card)
    self.card.advance()
    self.card.advance()
    self.card.advance()
    self.card.score()
    self.assertIsInstance(
        self.game.current_phase(),
        card01055.DecideCard01055)

  def test_use_install_ice_ability(self):
    self.install_and_score()
    # pylint: disable=E1101
    self.game.resolve_current_phase(
        self.game.current_phase().yes_action, None)
    self.assertIsInstance(
        self.game.current_phase(),
        card01055.PerformCard01055)
    self.assertEqual(1, self.corp.archives.size)
    self.assertEqual('Card01110', self.corp.archives.cards[0].NAME)
    choices = self.game.current_phase().choices()
    response = choices[0].request().new_response()
    server = self.corp.new_remote_server()
    response.server = server
    self.game.resolve_current_phase(choices[0], response)
    self.assertEqual(1, server.ice.size)
    self.assertTrue(server.ice.cards[0].is_rezzed)

    choices = self.game.current_phase().choices()
    response = choices[0].request().new_response()
    response.server = server
    self.game.resolve_current_phase(choices[0], response)
    self.assertEqual(2, server.ice.size)
    self.assertTrue(server.ice.cards[1].is_rezzed)
    self.assertEqual(6, self.corp.credits.value)

  def test_no_use_install_ice_ability(self):
    self.install_and_score()
    self.assertIsInstance(
        self.game.current_phase(),
        card01055.DecideCard01055)
    # pylint: disable=E1101
    self.game.resolve_current_phase(
        self.game.current_phase().no_action, None)
    self.assertIsInstance(
        self.game.current_phase(),
        timing_phases.CorpTurnActions)
    self.assertEqual(0, self.corp.archives.size)


if __name__ == '__main__':
  unittest.main()
