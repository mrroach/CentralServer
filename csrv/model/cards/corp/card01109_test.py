import unittest
from csrv.model import errors
from csrv.model import events
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.corp import card01109


class Card01109Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01109.Card01109(self.game, self.corp)
    self.corp.clicks.set(3)
    self.corp.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.CorpTurnActions(self.game, self.corp))

  def test_credit_gained_on_corp_turn_begin(self):
    server = self.corp.new_remote_server()
    server.install(self.card)
    self.assertEqual(6, self.corp.credits.value)
    self.card.rez()
    self.game.trigger_event(events.CorpTurnBegin(self.game, self.corp), None)
    self.assertEqual(7, self.corp.credits.value)

  def test_not_gained_if_not_rezzed(self):
    server = self.corp.new_remote_server()
    server.install(self.card)
    self.assertEqual(6, self.corp.credits.value)
    self.game.trigger_event(events.CorpTurnBegin, None)
    self.assertEqual(6, self.corp.credits.value)


if __name__ == '__main__':
  unittest.main()
