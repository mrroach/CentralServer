import unittest
from csrv.model import errors
from csrv.model import events
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.corp import card01065


class Card01065Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01065.Card01065(self.game, self.corp)
    self.corp.clicks.set(3)
    self.corp.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.CorpTurnAbilities(self.game, self.corp))
    self.server = self.corp.new_remote_server()
    self.other_server = self.corp.new_remote_server()
    ice = []
    for c in list(self.corp.hq.cards):
      self.corp.hq.remove(c)
      self.corp.rnd.add(c)
    for c in list(self.corp.rnd.cards):
      # 3-strength barrier
      if c.NAME == 'Card01113':
        self.corp.rnd.remove(c)
        ice.append(c)
    self.server.install_ice(ice[0])
    self.server.install_ice(ice[1])
    self.other_server.install_ice(ice[2])
    ice[0].rez()
    ice[2].rez()
    self.server.install(self.card)

  def test_boost_strength(self):
    choices = self.game.current_phase().choices()
    self.assertEqual(1, len(choices))
    self.game.resolve_current_phase(choices[0], None)

    # should be usable now
    choices = self.game.current_phase().choices()
    self.assertEqual([self.card._card01065_action], choices)

    self.game.resolve_current_phase(choices[0], None)

    choices = self.game.current_phase().choices()
    self.assertEqual(1, len(choices))
    response = choices[0].request().new_response()
    response.credits = 3
    self.game.resolve_current_phase(choices[0], response)
    self.assertEqual(6, self.server.ice.cards[0].strength)
    self.assertEqual(3, self.server.ice.cards[1].strength)
    self.assertEqual(3, self.other_server.ice.cards[0].strength)
    self.game.trigger_event(
        events.CorpDiscardPhase(self.game, self.corp), None)
    self.assertEqual(3, self.server.ice.cards[0].strength)


if __name__ == '__main__':
  unittest.main()
