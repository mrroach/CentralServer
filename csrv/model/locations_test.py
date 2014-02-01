import unittest
from csrv.model import deck
from csrv.model import events
from csrv.model import game
from csrv.model import modifiers


class TestLocation(unittest.TestCase):

  def setUp(self):
    self.corp_deck = deck.CorpDeck(
        'Haas-Bioroid: Engineering the Future',
        ['Adonis Campaign',
         'Adonis Campaign',
         'Adonis Campaign',
         'Hedge Fund',
         'Hedge Fund',
         'Hedge Fund',
         'Accelerated Beta Test',
         'Accelerated Beta Test',
         'Accelerated Beta Test',
         'Melange Mining Corp.',
         'Melange Mining Corp.',
         'Melange Mining Corp.'])
    self.runner_deck = deck.RunnerDeck(
        'Noise: Hacker Extraordinaire',
        ['Sure Gamble',
         'Yog.0',
         'Mimic',
         'Magnum Opus',
         'Armitage Codebusting',
        ])
    self.game = game.Game(self.corp_deck, self.runner_deck)


class TestHQ(TestLocation):
  """Test location object."""

  def setUp(self):
    TestLocation.setUp(self)
    self.hq = self.game.corp.hq
    self.game.corp.draw_starting_hand_and_credits()

  def testHqAccessReturnsOneHqCard(self):
    cards = self.hq.cards_to_access()
    self.assertEqual(1, len(cards))
    self.assertIn(cards[0], self.hq.cards)

  def testHqAllowsUpgradeAccess(self):
    upgrade = self.hq.cards[0]
    self.hq.install(upgrade)
    cards = self.hq.cards_to_access()
    self.assertEqual(2, len(cards))
    self.assertIn(upgrade, cards)

  def testHqHandlesAccessRestriction(self):
    upgrade = self.hq.cards[0]
    self.hq.install(upgrade)
    mod = modifiers.CardAccessRestriction(
        self.game, upgrade, server=self.hq)
    self.assertEqual([upgrade], self.hq.cards_to_access())

  def testHqHandlesAccessModifiers(self):
    mod = modifiers.NumHqCardsToAccess(
        self.game, 2, server=self.hq)
    cards = self.hq.cards_to_access()
    self.assertEqual(3, len(cards))

  def testHqHandlesRestrictionAndModifiers(self):
    upgrade = self.hq.cards[0]
    self.hq.install(upgrade)
    mod = modifiers.CardAccessRestriction(
        self.game, upgrade, server=self.hq)
    num_mod = modifiers.NumHqCardsToAccess(
        self.game, 2, server=self.hq)
    cards = self.hq.cards_to_access()
    self.assertEqual([upgrade], cards)


class TestRnd(TestLocation):
  """Test location object."""

  def setUp(self):
    TestLocation.setUp(self)
    self.rnd = self.game.corp.rnd
    self.hq = self.game.corp.hq
    self.game.corp.draw_starting_hand_and_credits()

  def testRndAccessReturnsTopCard(self):
    cards = self.rnd.rnd_cards_to_access()
    self.assertEqual(self.rnd.cards[-1:], cards)

  def testRndAllowsUpgradeAccess(self):
    upgrade = self.hq.cards[0]
    self.rnd.install(upgrade)
    cards = self.rnd.cards_to_access()
    self.assertEqual([upgrade], cards)
    cards = self.rnd.rnd_cards_to_access()
    self.assertEqual(self.rnd.cards[-1:], cards)

  def testRndHandlesAccessRestriction(self):
    upgrade = self.hq.cards[0]
    self.rnd.install(upgrade)
    mod = modifiers.CardAccessRestriction(
        self.game, upgrade, server=self.rnd)
    self.assertEqual([upgrade], self.rnd.cards_to_access())

  def testRndHandlesAccessModifiers(self):
    mod = modifiers.NumRndCardsToAccess(
        self.game, 2, server=self.rnd)
    cards = self.rnd.rnd_cards_to_access()
    self.assertEqual(self.rnd.cards[-3:], cards)

  def testRndHandlesRestrictionAndModifiers(self):
    upgrade = self.hq.cards[0]
    self.rnd.install(upgrade)
    mod = modifiers.CardAccessRestriction(
        self.game, upgrade, server=self.rnd)
    num_mod = modifiers.NumRndCardsToAccess(
        self.game, 2, server=self.rnd)
    cards = self.rnd.cards_to_access()
    self.assertEqual([upgrade], cards)


class RemoteServerTest(TestLocation):
  def setUp(self):
    TestLocation.setUp(self)
    self.server = self.game.corp.new_remote_server()

  def testServerIsRemovedWhenLastCardUninstalled(self):
    card = self.game.corp.rnd.pop()
    self.server.install(card)
    self.assertIn(self.server, self.game.corp.remotes)
    self.server.uninstall(card)
    self.assertNotIn(self.server, self.game.corp.remotes)

if __name__ == '__main__':
  unittest.main()
