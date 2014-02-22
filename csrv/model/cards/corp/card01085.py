from csrv.model import actions
from csrv.model import cost
from csrv.model import errors
from csrv.model import parameters
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import operation


class AdvanceVariableAmount(actions.Action):
  REQUEST_CLASS = parameters.VariableCreditCostRequest
  DESCRIPTION = 'Place X advancement tokens on this card'

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if not response or response.credits < 0:
      raise errors.InvalidResponse('You must choose an amount to spend')
    if response.credits > self.game.runner.tags:
      raise errors.InvalidResponse('You may not exceed the number of tags')
    self.cost = cost.SimpleCost(self.game, self.player,
                                credits=response.credits)
    actions.Action.resolve(
        self, response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.card.advancement_tokens += response.credits


class ChooseCardToAdvance(timing_phases.BasePhase):
  """Choose an advanceable card."""

  def __init__(self, game, player, card):
    timing_phases.BasePhase.__init__(self, game, player, both_players=False)
    self.card = card

  def choices(self, refresh=False):
    if not self._choices or refresh:
      self._choices = [AdvanceVariableAmount(self.game, self.player, card)
                       for card in self.card.advanceable_cards()]
    return self._choices

  def resolve(self, choice, response=None):
    timing_phases.BasePhase.resolve(self, choice, response)
    if choice:
      self.end_phase()


class Card01085(operation.Operation):

  NAME = u'Card01085'
  SET = card_info.CORE
  NUMBER = 85
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  INFLUENCE = 3
  UNIQUE = False
  COST = 0
  IMAGE_SRC = '01085.png'

  def build_actions(self):
    operation.Operation.build_actions(self)

  def play(self):
    operation.Operation.play(self)
    self.game.insert_next_phase(
        ChooseCardToAdvance(self.game, self.player, self))

  def is_playable(self):
    return (operation.Operation.is_playable(self) and
            bool(self.advanceable_cards()) and
            bool(self.game.runner.tags))

  def advanceable_cards(self):
    # TODO(mrroach): stop repeating this. Move it somewhere sensible
    targets = []
    for server in self.game.corp.servers:
      for card in server.ice.cards + server.installed.cards:
        if card.can_be_advanced():
          targets.append(card)
    return targets

