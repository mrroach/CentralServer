import unittest
from csrv.model import cards
from csrv.model.cards import corp
from csrv.model.cards import runner
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks


class TestBase(unittest.TestCase):
  CORP_DECK = 'RoboCorp Core'
  RUNNER_DECK = 'Anarchist Core'

  def setUp(self):
    corp_info = [d for d in premade_decks.corp_decks
                 if d['name'] == self.CORP_DECK][0]
    runner_info = [d for d in premade_decks.runner_decks
                   if d['name'] == self.RUNNER_DECK][0]
    self.corp_deck = deck.CorpDeck(corp_info['identity'], corp_info['cards'])
    self.runner_deck = deck.RunnerDeck(runner_info['identity'],
                                       runner_info['cards'])
    self.game = game.Game(self.corp_deck, self.runner_deck)
    self.corp = self.game.corp
    self.runner = self.game.runner
