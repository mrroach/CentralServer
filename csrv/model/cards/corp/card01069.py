from csrv.model import actions
from csrv.model import cost
from csrv.model import timing_phases
from csrv.model.cards import asset
from csrv.model.cards import card_info


class YesCard01069(actions.Action):
  DESCRIPTION = '1 [credit]: Do net damage'

  def __init__(self, game, player):
    cost_obj = cost.Cost(game, player, credits=1)
    actions.Action.__init__(self, game, player, cost=cost_obj)


class NoCard01069(actions.Action):
  DESCRIPTION = 'Do not do net damage'


class DecideCard01069(timing_phases.ActivateAbilityChoice):
  """Choose whether to use Card01069."""

  def __init__(self, game, player, next_phase):
    timing_phases.ActivateAbilityChoice.__init__(
        self, game, player,
        YesCard01069(game, player),
        NoCard01069(game, player),
        next_phase)


class Card01069(asset.Asset):

  NAME = u'Card01069'
  SET = card_info.CORE
  NUMBER = 69
  SIDE = card_info.CORP
  FACTION = card_info.NETCORP
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.AMBUSH,
      card_info.RESEARCH,
  ])
  ADVANCEABLE = True
  COST = 0
  IMAGE_SRC = '01069.png'
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
      phase = DecideCard01069(
          self.game, self.player,
          timing_phases.TakeNetDamage(self.game, self.game.runner,
                                      2 * self.advancement_tokens))
      self.game.insert_next_phase(phase)
      phase.begin()
