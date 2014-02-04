from csrv.model import actions
from csrv.model import cost
from csrv.model import errors
from csrv.model import parameters
from csrv.model.actions import subroutines
from csrv.model.actions.subroutines import trash_a_program
from csrv.model.cards import card_info
from csrv.model.cards import ice


class Card01101Cost(cost.RezIceCost):
  def can_pay(self):
    return (cost.RezIceCost.can_pay(self) and
            self.player.scored_agendas.size)

  def pay(self, response=None, ignore_clicks=False):
    if not response or not response.agenda:
      raise errors.CostNotSatisfied('You must forfeit an agenda to rez Card01101')
    if not response.agenda.location == self.player.scored_agendas:
      raise errors.InvalidResponse('You must forfeit a scored agenda')
    cost.RezIceCost.pay(self, response=response, ignore_clicks=ignore_clicks)
    self.player.scored_agendas.remove(response.agenda)


class RezCard01101(actions.RezIce):
  COST_CLASS = Card01101Cost
  REQUEST_CLASS = parameters.ForfeitAgendaRequest


class Card01101(ice.Ice):

  NAME = u'Card01101'
  SET = card_info.CORE
  NUMBER = 101
  SIDE = card_info.CORP
  FACTION = card_info.MEATCORP
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.DESTROYER,
      card_info.SENTRY,
  ])
  COST = 4
  IMAGE_SRC = '01101.png'
  STRENGTH = 6

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        subroutines.CorpGainsCredits(self.game, self.player, 2),
        trash_a_program.TrashAProgram(self.game, self.player),
        trash_a_program.TrashAProgram(self.game, self.player),
        subroutines.EndTheRun(self.game, self.player),
    ]

  def build_actions(self):
    ice.Ice.build_actions(self)
    self._rez_action = RezCard01101(self.game, self.player, self)

