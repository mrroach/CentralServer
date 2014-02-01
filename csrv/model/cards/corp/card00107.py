from csrv.model import actions
from csrv.model import cost
from csrv.model import timing_phases
from csrv.model.cards import agenda
from csrv.model.cards import card_info


class DoMeatDamage(actions.Action):
  """Do meat damage to the runner."""

  DESCRIPTION = '[Click] Do 1 meat damage'

  def __init__(self, game, player, card=None):
    cost_obj = cost.Cost(game, player, clicks=1)
    actions.Action.__init__(self, game, player, card=card, cost=cost_obj)

  def is_usable(self):
    return actions.Action.is_usable(self) and self.game.runner.tags

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.Action.resolve(
        self, response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.game.insert_next_phase(
        timing_phases.TakeMeatDamage(self.game, self.game.runner, 1))


class Card00107(agenda.Agenda):

  NAME = u'Card00107'
  SET = card_info.CORE
  NUMBER = 107
  SIDE = card_info.CORP
  FACTION = card_info.NEUTRAL
  INFLUENCE = 0
  UNIQUE = False
  KEYWORDS = set([
      card_info.SECURITY,
  ])
  ADVANCEMENT_REQUIREMENT = 4
  AGENDA_POINTS = 2
  IMAGE_SRC = '01107.png'

  WHEN_IN_CORP_SCORE_AREA_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpTurnActions: 'meat_damage_actions',
  }

  def build_actions(self):
    agenda.Agenda.build_actions(self)
    self._do_meat_damage = DoMeatDamage(
        self.game, self.player, card=self)

  def meat_damage_actions(self):
    return [self._do_meat_damage]
