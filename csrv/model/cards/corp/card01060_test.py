import unittest
from csrv.model import errors
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.corp import card01060


class Card01060Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01060.Card01060(self.game, self.corp)
    self.corp.clicks.set(3)
    self.corp.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.CorpTurnActions(self.game, self.corp))
    for card in list(self.corp.hq.cards):
      self.corp.hq.remove(card)
      self.corp.rnd.add(card)
    for card in list(self.corp.rnd.cards):
      if card.NAME == 'Card01113':
        self.corp.hq.add(card)
    self.corp.hq.add(self.card)

  def test_card_allows_installing(self):
    self.game.resolve_current_phase(self.card._play_operation_action, None)
    self.assertIsInstance(self.game.current_phase(), card01060.Card01060Phase)
    actions = [c.install_action for c in self.corp.hq.cards]
    self.assertItemsEqual(actions, self.game.current_phase().choices())
    self.assertEqual(2, self.corp.clicks.value)

    # Install the first card in a new server
    response = actions[0].request().new_response()
    self.game.resolve_current_phase(actions[0], response)

    self.assertItemsEqual(actions[1:], self.game.current_phase().choices())
    self.assertEqual(2, self.corp.clicks.value)

    # Install the last card in the same server
    response = actions[2].request().new_response()
    response.server = self.corp.remotes[0]
    self.game.resolve_current_phase(actions[2], response)
    self.assertEqual(4, self.corp.credits.value)

    # let's not install any more things.
    self.game.resolve_current_phase(None, None)
    self.assertIsInstance(
        self.game.current_phase(), timing_phases.CorpTurnAbilities)
    self.assertEqual(2, self.corp.clicks.value)


if __name__ == '__main__':
  unittest.main()
