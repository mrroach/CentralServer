from csrv.model.cards import asset
from csrv.model.cards import card_info
from csrv.model import cost
from csrv.model import actions
from csrv.model import timing_phases


class Card01108(asset.Asset):

  NAME = 'Card01108'
  SUBTYPES = []
  COST = 1
  TRASH_COST = 1
  FACTION = card_info.NEUTRAL
  INFLUENCE = 0
  SET = card_info.CORE
  SIDE = card_info.CORP
  NUMBER = 108
  IMAGE_SRC = '01108.png'

  WHEN_REZZED_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpTurnActions: 'gain_credits_actions',
  }

  def build_actions(self):
    asset.Asset.build_actions(self)
    self._gain_credits_ability = actions.CardClickAbility(
        self.game, self.player, self,
        '[Click],[Click],[Click]: Gain 7[Credits]', 'gain_credits',
          cost=cost.SimpleCost(self.game, self.player, clicks=3))

  def gain_credits_actions(self):
    return [self._gain_credits_ability]

  def gain_credits(self):
    self.player.credits.gain(7)

