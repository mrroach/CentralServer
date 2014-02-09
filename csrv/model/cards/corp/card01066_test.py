import unittest
from csrv.model import errors
from csrv.model import events
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.corp import card01066


class Card01066Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01066.Card01066(self.game, self.corp)
    self.corp.clicks.set(3)
    self.corp.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.CorpTurnActions(self.game, self.corp))
    for c in list(self.corp.rnd.cards):
      # 3 strength barrier
      if c.NAME == 'Card01113':
        self.corp.rnd.remove(c)
        self.ice = c
        break

  def test_strength_increased(self):
    server = self.corp.new_remote_server()
    server.install_ice(self.ice)
    self.assertEqual(3, self.ice.strength)
    server.install(self.card)
    self.card.rez()
    self.assertEqual(4, self.ice.strength)
    self.card.trash()
    self.assertEqual(3, self.ice.strength)


if __name__ == '__main__':
  unittest.main()
