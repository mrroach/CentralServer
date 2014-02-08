import unittest
from csrv.model import cards
from csrv.model.cards import corp
from csrv.model.cards import runner
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks


class TestBase(unittest.TestCase):

  def setUp(self):
    self.corp_deck = deck.CorpDeck(
        premade_decks.corp_decks[0]['identity'],
        premade_decks.corp_decks[0]['cards'])
    self.runner_deck = deck.RunnerDeck(
        premade_decks.runner_decks[0]['identity'],
        premade_decks.runner_decks[0]['cards'])
    self.game = game.Game(self.corp_deck, self.runner_deck)
    self.corp = self.game.corp
    self.runner = self.game.runner
