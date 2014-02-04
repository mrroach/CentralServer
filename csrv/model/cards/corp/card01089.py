from csrv.model import actions
from csrv.model import events
from csrv.model import timing_phases
from csrv.model.actions.subroutines import trace_for_tag
from csrv.model.cards import card_info
from csrv.model.cards import ice


class AdvanceCard(actions.AdvanceCard):
  def __init__(self, game, player, card, analyzer):
    cost_obj = cost.Cost(credits=1)
    actions.AdvanceCard.__init__(self, game, player, card=card, cost=cost_obj)
    self.analyzer = analyzer
    self._choice_made = False

  def is_usable(self):
    return not self._choice_made

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.AdvanceCard.resolve(
        self,
        response=response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.analyzer.choice_made()

  def choice_made(self):
    self._choice_made = True


class Card01089(ice.Ice):

  NAME = u'Card01089'
  SET = card_info.CORE
  NUMBER = 89
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.OBSERVER,
      card_info.SENTRY,
      card_info.TRACER,
  ])
  COST = 1
  IMAGE_SRC = '01089.png'
  STRENGTH = 3
  WHEN_INSTALLED_LISTENS = [
      events.BeginEncounterIce_3_1,
  ]
  WHEN_REZZED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'advance_actions',
  }

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        trace_for_tag.TraceForTag(game, player, base_strength=2)
    ]

  def build_actions(self):
    ice.Ice.build_actions(self)
    self._advance_actions = []

  def on_begin_encounter_ice_3_1(self, sender, event):
    advance = []
    for server in self.game.corp.servers:
      for card in server.installed.cards + server.ice.cards:
        if card.can_be_advanced():
          advance.append(AdvanceCard(self.game, self.player, card, self))
    self._advance_actions = advance

  def advance_actions(self):
    if self.game.run and self.game.run.current_ice() == self:
      return self._advance_actions
    else:
      return []

  def choice_made(self):
    for action in self._advance_Actions:
      action.choice_made()
