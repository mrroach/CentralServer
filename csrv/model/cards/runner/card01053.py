from csrv.model import actions
from csrv.model.cards import card_info
from csrv.model.cards import resource
from csrv.model import cost
from csrv.model import pool
from csrv.model import timing_phases


class Card01053(resource.Resource):

  NAME = u'Card01053'
  SET = card_info.CORE
  NUMBER = 53
  SIDE = card_info.RUNNER
  FACTION = card_info.NEUTRAL
  INFLUENCE = 0
  UNIQUE = False
  KEYWORDS = set([
      card_info.JOB,
  ])
  COST = 1
  IMAGE_SRC = '01053.png'
  ABILITIES = [
      '[Click]: Take 2[Credits] from Card01053.'
  ]


  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
    timing_phases.RunnerTurnActions: 'gain_credits_actions',
  }

  def __init__(self, game, player):
    resource.Resource.__init__(self, game, player)
    self.pool = None

  @property
  def credits(self):
    if self.pool:
      return self.pool.value
    return 0

  def build_actions(self):
    resource.Resource.build_actions(self)
    self._gain_credits_ability = actions.CardClickAbility(
        self.game, self.player, self, self.ABILITIES[0], 'gain_credits',
        cost=cost.BasicActionCost(self.game, self.player))

  def on_install(self):
    resource.Resource.on_install(self)
    self.pool = pool.CreditPool(self.game, self.player, 12)

  def gain_credits_actions(self):
    return [self._gain_credits_ability]

  def gain_credits(self):
    self.pool.lose(2)
    self.player.credits.gain(2)
    if not self.pool.value:
      self.pool = None
      self.trash()
