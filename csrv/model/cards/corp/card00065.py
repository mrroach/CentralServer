from csrv.model import actions
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import modifiers
from csrv.model import parameters
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import upgrade


class BoostIceStrengthAction(actions.Action):
  REQUEST_CLASS = parameters.VariableCreditCostRequest

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if not response or response.credits < 0:
      raise errors.InvalidResponse('You must choose an amount to spend')
    self.cost = cost.SimpleCost(self.game, self.player,
                                credits=response.credits)
    actions.Action.resolve(
        self, response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    modifiers.IceStrengthModifier(
        self.game, response.credits,
        card=self.card, until=events.CorpDiscardPhase)


class ChooseIceToBoost(timing_phases.BasePhase):
  """Choose a piece of rezzed ice protecting this server."""
  NULL_OK = False

  def __init__(self, game, player, server):
    timing_phases.BasePhase.__init__(self, game, player)
    self.server = server

  def choices(self, refresh=False):
    if self._choices is None or refresh:
      self._choices = []
      for ice in self.server.ice.cards:
        if ice.is_rezzed:
          self._choices.append(
              BoostIceStrengthAction(self.game, self.player, ice))
    return self._choices

  def resolve(self, choice, response):
    timing_phases.BasePhase.resolve(self, choice, response)
    if choice:
      self.end_phase()


class Card00065Action(actions.Action):
  DESCRIPTION = 'Trash card00065 and choose ice to boost'
  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.Action.resolve(
        self, response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.game.insert_next_phase(
        ChooseIceToBoost(self.game, self.player,
                         server=self.card.location.parent))
    self.card.trash()


class Card00065(upgrade.Upgrade):

  NAME = u'Card00065'
  SET = card_info.CORE
  NUMBER = 65
  SIDE = card_info.CORP
  FACTION = card_info.ROBOCORP
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.CONNECTION,
  ])
  COST = 0
  IMAGE_SRC = '01065.png'
  TRASH_COST = 2

  WHEN_REZZED_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpUseAbilities: 'card00065_actions',
  }

  def build_actions(self):
    upgrade.Upgrade.build_actions(self)
    self._card00065_action = Card00065Action(
      self.game, self.player, card=self)

  def card00065_actions(self):
    return [self._card00065_action]
