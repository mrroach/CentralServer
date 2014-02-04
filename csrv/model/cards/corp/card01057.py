from csrv.model import actions
from csrv.model import cost
from csrv.model import errors
from csrv.model import timing_phases
from csrv.model.cards import asset
from csrv.model.cards import program
from csrv.model.cards import card_info


class YesCard01057(actions.Action):
  DESCRIPTION = 'Use Card01057'

  def __init__(self, game, player):
    cost_obj = cost.SimpleCost(game, player, credits=2)
    actions.Action.__init__(self, game, player, cost=cost_obj)


class NoCard01057(actions.Action):
  DESCRIPTION = 'Do not use Card01057'


class DecideCard01057(timing_phases.ActivateAbilityChoice):
  """Choose whether to use Card01057."""

  def __init__(self, game, player, next_phase):
    timing_phases.ActivateAbilityChoice.__init__(
        self, game, player,
        YesCard01057(game, player),
        NoCard01057(game, player),
        next_phase)


class Card01057Phase(timing_phases.BasePhase):
  """Trash 1 program for each advancement token on Card01057."""
  NULL_OK = False

  def __init__(self, game, player, card):
    timing_phases.BasePhase.__init__(self, game, player, both_players=False)
    self._max_choices = card.advancement_tokens
    self._num_chosen = 0
    self._chosen = set()

  def choices(self, refresh=False):
    if self._choices is None or refresh:
      # The card can be chosen multiple times
      programs = [card for card in self.game.runner.rig.cards
                  if isinstance(card, program.Program)]
      self._choices = [
          actions.Trash(self.game, self.player, card) for card in programs]
    return self._choices

  def resolve(self, choice, response):
    if choice:
      self._chosen.add(choice)
      self._num_chosen += 1
    else:
      raise errors.ChoiceRequiredError('You must choose one of the options')
    if self._num_chosen == self._max_choices:
      for c in self._chosen:
        c.resolve(None)
      self.end_phase()


class Card01057(asset.Asset):

  NAME = u'Card01057'
  SET = card_info.CORE
  NUMBER = 57
  SIDE = card_info.CORP
  FACTION = card_info.ROBOCORP
  INFLUENCE = 2
  UNIQUE = False
  ADVANCEABLE = True
  KEYWORDS = set([
      card_info.AMBUSH,
  ])
  COST = 0
  IMAGE_SRC = '01057.png'
  TRASH_COST = 0

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpTurnActions: 'installed_actions',
  }

  def build_actions(self):
    asset.Asset.build_actions(self)
    self._advance_action = actions.AdvanceCard(self.game, self.player, self)

  def installed_actions(self):
    return [self._advance_action]

  def on_access(self):
    asset.Asset.on_access(self)
    if self.advancement_tokens:
      phase = DecideCard01057(
          self.game, self.player,
          Card01057Phase(self.game, self.player, self))
      self.game.insert_next_phase(phase)
      phase.begin()

