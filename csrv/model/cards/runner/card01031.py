from csrv.model import actions
from csrv.model import cost
from csrv.model import errors
from csrv.model import parameters
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import resource


class Card01031Cost(cost.BasicActionCost):
  def can_pay(self):
    return (cost.BasicActionCost.can_pay(self) and
            self.player.scored_agendas.size)

  def pay(self, response=None, ignore_clicks=False):
    if not response or not response.agenda:
      raise errors.CostNotSatisfied('You must forfeit an agenda')
    if not response.agenda.location == self.player.scored_agendas:
      raise errors.InvalidResponse('You must forfeit a scored agenda')
    cost.BasicActionCost.pay(
        self, response=response, ignore_clicks=ignore_clicks)
    # TODO(mrroach): This should probably happen automatically when an agenda
    # is removed from the score area. probably via on_enter_*_score_area
    self.player.scored_agendas.remove(response.agenda)
    self.player.agenda_points -= response.agenda.agenda_points


class ForfeitAgenda(actions.Action):
  REQUEST_CLASS = parameters.ForfeitAgendaRequest
  DESCRIPTION = 'Forfeit an agenda, [click]: gain 9 [credits]'
  COST_CLASS = Card01031Cost

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.Action.resolve(
        self, response=response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.player.credits.gain(9)


class Card01031(resource.Resource):

  NAME = u'Card01031'
  SET = card_info.CORE
  NUMBER = 31
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.CONNECTION,
      card_info.SEEDY,
  ])
  COST = 0
  IMAGE_SRC = '01031.png'

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnActions: 'forfeit_agenda_actions',
  }

  def build_actions(self):
    resource.Resource.build_actions(self)
    self._forfeit_agenda = ForfeitAgenda(self.game, self.player, card=self)

  def forfeit_agenda_actions(self):
    return [self._forfeit_agenda]
