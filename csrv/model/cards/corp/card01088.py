from csrv.model import actions
from csrv.model import events
from csrv.model import timing_phases
from csrv.model.actions.subroutines import trace
from csrv.model.cards import card_info
from csrv.model.cards import ice


class TraceForPowerCounter(trace.Trace):
  DESCRIPTION = 'Trace 3 - if successful, place 1 power counter on Card01088'

  def on_success(self, corp_total, runner_total):
    self.card.power_counters += 1


class GiveATag(actions.Action):
  DESCRIPTION = 'Give the runner 1 tag'

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    self.card.power_counters -= 1
    self.game.insert_next_phase(
        timing_phases.TakeTags(self.game, self.game.runner, 1))


class TakeATag(actions.Action):
  DESCRIPTION = 'Take a tag'

  def __init__(self, game, player, card=None):
    actions.Action.__init__(self, game, player, card=card)
    self._is_mandatory = True
    self._choice_made = False

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    self.game.runner.tags += 1
    self.card.log('The runner takes a tag from Card01088')
    self.card.choice_made()

  def choice_made(self):
    self._choice_made = True

  def is_usable(self):
    return not self._choice_made


class JackOut(actions.JackOut):
  def __init__(self, game, player, run, card=None):
    actions.JackOut.__init__(self, game, player, run, card=card)
    self._choice_made = False

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.JackOut.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.card.choice_made()

  def choice_made(self):
    self._choice_made = True

  def is_usable(self):
    return not self._choice_made


class Card01088(ice.Ice):

  NAME = u'Card01088'
  SET = card_info.CORE
  NUMBER = 88
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.OBSERVER,
      card_info.SENTRY,
      card_info.TRACER,
  ])
  COST = 4
  IMAGE_SRC = '01088.png'
  STRENGTH = 4
  WHEN_REZZED_PROVIDES_CHOICES_FOR = {
      timing_phases.EncounterIce_3_1: 'encounter_actions',
      timing_phases.CorpUseAbilities: 'card01088_abilities',
  }
  WHEN_INSTALLED_LISTENS = [
      events.BeginEncounterIce_3_1
  ]

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        TraceForPowerCounter(self.game, self.player, card=self)
    ]
    self._encounter_actions = []

  def on_begin_encounter_ice_3_1(self, sender, event):
    self._encounter_actions = [
        TakeATag(self.game, self.game.runner, card=self),
        JackOut(self.game, self.game.runner, self.game.run, card=self)
    ]

  def encounter_actions(self):
    if self.game.run and self.game.run.current_ice() == self:
      return self._encounter_actions
    else:
      return []

  def choice_made(self):
    for action in self._encounter_actions:
      action.choice_made()

  def card01088_abilities(self):
    actions = []
    if self.power_counters:
      actions.append(GiveATag(self.game, self.player, card=self))
    return actions
