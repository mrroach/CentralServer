from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import asset
from csrv.model.cards import card_info


class YesCard01087(actions.Action):
  DESCRIPTION = 'Give the runner tags'

  def __init__(self, game, player, advancements):
    self.advancements = advancements

  def resolve(self, response=None):
    self.game.runner.tags += self.advancements


class NoCard01087(actions.Action):
  DESCRIPTION = 'Do not give the runner tags'


class DecideCard01087(timing_phases.ActivateAbilityChoice):
  """Choose whether to use Card01087."""

  def __init__(self, game, player, advancements):
    timing_phases.ActivateAbilityChoice.__init__(
        self, game, player,
        YesCard01087(game, player, advancements),
        NoCard01087(game, player),
        None)


class Card01087(asset.Asset):

  NAME = u'Card01087'
  SET = card_info.CORE
  NUMBER = 87
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.AMBUSH,
      card_info.FACILITY,
  ])
  COST = 0
  ADVANCEABLE = True
  IMAGE_SRC = '01087.png'
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
    if self.is_installed and self.advancement_tokens:
      phase = DecideCard01087(
          self.game, self.player, self.advancement_tokens)
      self.game.insert_next_phase(phase)
      phase.begin()

