import unittest
from csrv.model import errors
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.corp import card01058


class Card01058Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01058.Card01058(self.game, self.corp)
    self.corp.clicks.set(3)
    self.corp.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.CorpTurnActions(self.game, self.corp))

  def test_not_playable_when_archives_empty(self):
    self.corp.hq.add(self.card)
    self.assertNotIn(
        self.card._play_operation_action, self.game.current_phase().choices())

  def test_playable_when_card_in_archive(self):
    self.corp.hq.cards[0].trash()
    self.corp.hq.add(self.card)
    self.assertIn(
        self.card._play_operation_action, self.game.current_phase().choices())

  def test_cannot_retrieve_card_from_rnd(self):
    self.corp.hq.cards[0].trash()
    self.corp.hq.add(self.card)
    response = self.card._play_operation_action.request().new_response()
    response.cards.append(self.corp.hq.cards[0])
    self.assertRaises(
        errors.InvalidResponse,
        self.game.resolve_current_phase,
        self.card._play_operation_action, response)

  def test_can_retrieve_card_from_archives(self):
    trashed = self.corp.hq.cards[0]
    trashed.trash()
    self.corp.hq.add(self.card)
    response = self.card._play_operation_action.request().new_response()
    response.cards.append(trashed)
    self.game.resolve_current_phase(
        self.card._play_operation_action, response)
    self.assertIn(trashed, self.corp.hq.cards)



if __name__ == '__main__':
  unittest.main()
