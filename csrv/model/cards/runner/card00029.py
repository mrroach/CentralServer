from csrv.model import actions
from csrv.model import errors
from csrv.model import parameters
from csrv.model import pool
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import resource


class ChooseCard00029Amount(actions.Action):
  DESCRIPTION = 'Choose how much money to take from Card00029'
  REQUEST_CLASS = parameters.NumericChoiceRequest

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if (not response or response.number < 0
        or response.number > self.card.pool.value):
      raise errors.InvalidResponse(
          'You must choose a number between 0 and %d' %
          self.card.pool.value)
    self.card.take_credits(response.number)


class TakeMoneyPhase(timing_phases.BasePhase):
  """Take money from Card00029."""
  NULL_OK = False

  def __init__(self, game, player, card=None):
    timing_phases.BasePhase.__init__(self, game, player, both_players=False)
    self.card = card

  def choices(self, refresh=False):
    return [ChooseCard00029Amount(self.game, self.player, card=self.card)]

  def resolve(self, choice, response=None):
    timing_phases.BasePhase.resolve(self, choice, response=response)
    if choice:
      self.end_phase()


class Card00029(resource.Resource):

  NAME = u'Card00029'
  SET = card_info.CORE
  NUMBER = 29
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.JOB,
  ])
  COST = 1
  IMAGE_SRC = '01029.png'

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.SelectAccessPhase: 'alternate_access_actions',
  }

  def __init__(self, game, player):
    resource.Resource.__init__(self, game, player)
    self.pool = None

  def on_install(self):
    resource.Resource.on_install(self)
    self.pool = pool.CreditPool(self.game, self.player, 8)

  @property
  def credits(self):
    if self.pool:
      return self.pool.value
    return 0

  def take_credits(self, credits):
    self.pool.lose(credits)
    self.player.credits.gain(credits)
    if not self.pool.value:
      self.pool = None
      self.trash()

  def build_actions(self):
    resource.Resource.build_actions(self)
    self._take_money_phase = TakeMoneyPhase(self.game, self.player, card=self)
    self._begin_take_money_phase = actions.NewTimingPhase(
        self.game, self.player, card=self, phase=self._take_money_phase,
        description='Take money from Card00029')

  def alternate_access_actions(self):
    if self.game.run and self.game.run.server in self.game.corp.remotes:
      return [self._begin_take_money_phase]
    return []
