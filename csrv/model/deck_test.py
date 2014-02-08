import unittest
from csrv.model import test_base
from csrv.model import deck
from csrv.model import premade_decks
from csrv.model import invalid_decks

class DeckTest(test_base.TestBase):
  def setUp(self):
    self.corp_deck = deck.CorpDeck(
        premade_decks.corp_decks[0]['identity'],
        premade_decks.corp_decks[0]['cards'])
    self.runner_deck = deck.RunnerDeck(
        premade_decks.runner_decks[0]['identity'],
        premade_decks.runner_decks[0]['cards'])

  def test_valid_decks(self):
    self.assertEqual(0, len(self.corp_deck.validate()))
    self.assertEqual(0, len(self.runner_deck.validate()))

  def test_minimum_deck_size(self):
    """corp deck over max"""
    self.corp_deck.cards = self.corp_deck.cards[0:self.corp_deck.identity.MIN_DECK_SIZE + 10]
    err = self.corp_deck.validate()
    self.assertEqual(0, len(err), err)
    """corp deck under max"""
    corp = deck.CorpDeck(
        invalid_decks.corp_decks['too_small']['identity'],
        invalid_decks.corp_decks['too_small']['cards'])
    self.assertEqual(1, len(corp.validate()))

    """runner deck over max"""
    self.runner_deck.cards = self.runner_deck.cards[0:self.runner_deck.identity.MIN_DECK_SIZE + 10]
    err = self.runner_deck.validate()
    self.assertEqual(0, len(err), err)
    """runner deck under max"""
    runner = deck.RunnerDeck(
        invalid_decks.runner_decks['too_small']['identity'],
        invalid_decks.runner_decks['too_small']['cards'])
    self.assertEqual(1, len(runner.validate()))

  def test_max_influence_points(self):
    d = deck.CorpDeck(
        invalid_decks.corp_decks['too_much_influence']['identity'],
        invalid_decks.corp_decks['too_much_influence']['cards'])
    self.assertEqual(1, len(d.validate()))

  def test_more_than_three_copies_of_card(self):
    pass

  def test_corp_too_few_agenda_points(self):
    d = deck.CorpDeck(
        invalid_decks.corp_decks['too_few_agenda_points']['identity'],
        invalid_decks.corp_decks['too_few_agenda_points']['cards'])
    self.assertEqual(1, len(d.validate()))

  def test_corp_out_of_faction_agendas(self):
    pass

  def test_corp_deck_cant_have_runner_cards(self):
    pass

  def test_runner_deck_cant_have_corp_cards(self):
    pass

if __name__ == '__main__':
  unittest.main()
