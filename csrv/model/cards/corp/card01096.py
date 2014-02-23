from csrv.model import actions
from csrv.model import cost
from csrv.model import timing_phases
from csrv.model.cards import asset
from csrv.model.cards import card_info


class Card01096(asset.Asset):

  NAME = u'Card01096'
  SET = card_info.CORE
  NUMBER = 96
  SIDE = card_info.CORP
  FACTION = card_info.MEATCORP
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.TRANSACTION,
  ])
  COST = 0
  IMAGE_SRC = '01096.png'
  TRASH_COST = 3

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpTurnActions: 'trash_actions',
  }

  def build_actions(self):
    asset.Asset.build_actions(self)
    #self._trash_ice_action = BeginTrashIcePhase(
    #    self.game, self.player, self)

  def trash_actions(self):
    return []

  def rezzed_ice(self):
    rezzed = []
    for server in self.game.corp.servers:
      for ice in server.ice:
        if ice.is_rezzed:
          rezzed.append(ice)
    return rezzed
