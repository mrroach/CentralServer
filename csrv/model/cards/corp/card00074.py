from csrv.model.actions.subroutines import subroutine
from csrv.model.cards import card_info
from csrv.model.cards import ice


class ApproachOutermostIceAndDerez(subroutine.Subroutine):
  DESCRIPTION = ('The Runner approaches the outermost piece of ice '
                 'protecting the attacked server. Derez Card00074.')

  def resolve(self, response=None):
    subroutine.Subroutine.resolve(self, response=response)
    self.card.log('The Runner approaches the outermost piece of ice.')
    # passing this piece of ice will cause position to be incremented
    self.card.derez()
    self.game.run.runner_position = -1


class Card00074(ice.Ice):

  NAME = u'Card00074'
  SET = card_info.CORE
  NUMBER = 74
  SIDE = card_info.CORP
  FACTION = card_info.NETCORP
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.CODE_GATE,
      card_info.DEFLECTOR,
  ])
  COST = 5
  IMAGE_SRC = '01074.png'
  STRENGTH = 7

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        ApproachOutermostIceAndDerez(self.game, self.player, card=self)
    ]

  def build_actions(self):
    ice.Ice.build_actions(self)
