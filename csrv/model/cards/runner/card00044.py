from csrv.model import actions
from csrv.model import cost
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import program


class Card00044(program.Program):

  NAME = u'Card00044'
  SET = card_info.CORE
  NUMBER = 44
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 2
  UNIQUE = False
  COST = 5
  MEMORY = 2
  IMAGE_SRC = '01044.png'
  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnActions: 'card_click_abilities',
  }

  def build_actions(self):
    program.Program.build_actions(self)
    self._gain_credits = actions.CardClickAbility(
        self.game, self.player, self, '[Click]: Gain 2[Credits]',
        'gain_credits', cost=cost.BasicActionCost(self.game, self.player))

  def card_click_abilities(self):
    return [self._gain_credits]

  def gain_credits(self):
    self.player.credits.gain(2)

