import unittest
from csrv.model import cards
from csrv.model.cards import corp
from csrv.model.cards import runner
from csrv.model import deck
from csrv.model import errors
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases
from csrv.model.cards.runner import card01031


class Card01031Test(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01031.Card01031(self.game, self.game.runner)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.runner.grip.add(self.card)
    self.game.insert_next_phase(
        timing_phases.RunnerTurnActions(self.game, self.game.runner))

  def test_playable(self):
    self.assertIn(self.card.install_action,
        self.game.current_phase().choices())

  def test_forfeit_for_money(self):
    self.runner.rig.add(self.card)
    self.assertNotIn(self.card._forfeit_agenda,
                     self.game.current_phase().choices())
    agenda = cards.Registry.get('Card01106')(self.game, self.game.corp)
    self.runner.scored_agendas.add(agenda)
    self.assertIn(self.card._forfeit_agenda,
                     self.game.current_phase().choices(refresh=True))
    request = self.card._forfeit_agenda.request()
    self.assertIn(agenda.game_id, request.valid_response_options()['agendas'])
    response = request.new_response()
    response.agenda = agenda
    self.game.resolve_current_phase(
        self.card._forfeit_agenda, response)
    self.assertEqual(14, self.runner.credits.value)


if __name__ == '__main__':
  unittest.main()
