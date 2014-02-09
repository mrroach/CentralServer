import unittest
from csrv.model.cards.corp import card01108
from csrv.model import deck
from csrv.model import game
from csrv.model import premade_decks
from csrv.model import test_base
from csrv.model import timing_phases


class TestCard01108(test_base.TestBase):

  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = card01108.Card01108(self.game, self.game.corp)
    self.game.corp.clicks.set(3)
    self.game.corp.credits.set(5)
    self.game.runner.clicks.set(4)
    self.game.runner.credits.set(5)
    self.game.insert_next_phase(
        timing_phases.CorpTurnActions(self.game, self.game.corp))
    self.game.corp.hq.add(self.card)
    self.game.insert_next_phase(
        timing_phases.CorpTurnActions(self.game, self.game.corp))

  def test_card(self):
    # I hate to have everything in one test, but each step depends on the one
    # before it, so there you go.

    # verify that card is installable
    self.assertIn(
        self.card.install_action, self.game.current_phase().choices())
    self.game.resolve_current_phase(self.card.install_action, None)

    # verify no cost charged (and identity credit gained)
    self.assertEqual(6, self.game.corp.credits.value)

    # verify card is installed
    self.assertIn(self.card, self.game.corp.remotes[0].installed.cards)
    self.assertTrue(self.card.is_installed)

    # resolve abilities
    self.assertIn(
        self.card._rez_action, self.game.current_phase().choices())
    self.game.resolve_current_phase(self.card._rez_action, None)
    self.assertEqual(5, self.game.corp.credits.value)

    self.game.insert_next_phase(
        timing_phases.CorpTurnActions(self.game, self.game.corp))

    # verify that credit gain ability is available
    self.assertNotIn(
        self.card._gain_credits_ability, self.game.current_phase().choices())
    self.game.corp.clicks.set(3)
    self.assertIn(
        self.card._gain_credits_ability,
        self.game.current_phase().choices(refresh=True))

    # verify that the gain credit ability works
    self.game.resolve_current_phase(self.card._gain_credits_ability, None)
    self.assertEqual(0, self.game.corp.clicks.value)
    self.assertEqual(12, self.game.corp.credits.value)


if __name__ == '__main__':
  unittest.main()
