from csrv.model import actions
from csrv.model import cost
from csrv.model import timing_phases
from csrv.model.cards import agenda
from csrv.model.cards import card_info


class Card01081AdvanceAction(actions.AdvanceCard):
  COST_CLASS = cost.NullCost

  def __init__(self, game, player, card, card01081):
    actions.AdvanceCard.__init__(self, game, player, card=card)
    self.card01081 = card01081

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.AdvanceCard.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.card01081.agenda_counters -= 1

  @property
  def description(self):
    return 'Use Card01081 token to advance %s' % self.card.NAME


class Card01081(agenda.Agenda):

  NAME = u'Card01081'
  SET = card_info.CORE
  NUMBER = 81
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  UNIQUE = False
  KEYWORDS = set([
      card_info.INITIATIVE,
  ])
  ADVANCEMENT_REQUIREMENT = 3
  AGENDA_POINTS = 2
  IMAGE_SRC = '01081.png'

  WHEN_IN_CORP_SCORE_AREA_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpUseAbilities: 'card01081_advance_actions',
  }

  def card01081_advance_actions(self):
    actions = []
    if self.agenda_counters:
      for server in self.game.corp.servers:
        for card in server.installed.cards + server.ice.cards:
          if card.can_be_advanced():
            actions.append(
                Card01081AdvanceAction(self.game, self.player, card, self))
    return actions

  def score(self):
    agenda.Agenda.score(self)
    self.agenda_counters += 1

