from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import event


class ChooseUnrezzedIce(timing_phases.BasePhase):
  """Choose unrezzed ice to force the corp to rez or trash it."""
  NULL_OK = False

  def __init__(self, game, player, card):
    timing_phases.BasePhase.__init__(self, game, player, both_players=False)
    self.card = card

  def choices(self, refresh=False):
    if not self._choices or refresh:
      self._choices = self.card.force_rez_actions()
    return self._choices

  def resolve(self, choice, response=None):
    timing_phases.BasePhase.resolve(self, choice, response)
    if choice:
      self.end_phase()


class ForceRezAction(actions.Action):
  """Force the corp to rez or trash ice."""

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.Action.resolve(self, response,
                           ignore_clicks=ignore_clicks,
                           ignore_all_costs=ignore_all_costs)
    self.game.insert_next_phase(
        RezOrTrash(self.game, self.game.corp, self.card))


class RezOrTrash(timing_phases.BasePhase):
  """Decide whether to rez ice or trash it."""
  DEFAULT = 'Trash the ice'

  def __init__(self, game, player, ice):
    timing_phases.BasePhase.__init__(self, game, player)
    self.ice = ice

  def choices(self, refresh=False):
    if not self._choices or refresh:
      self._choices = self.ice.rez_actions()
    return self._choices

  def resolve(self, choice, response=None):
    timing_phases.BasePhase.resolve(self, choice, response)
    if choice:
      self.end_phase()
    else:
      self.game.log('The corp chooses to trash the ice.')
      self.ice.trash()


class Card01020(event.Event):

  NAME = u'Card01020'
  SET = card_info.CORE
  NUMBER = 20
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.SABOTAGE,
  ])
  COST = 1
  IMAGE_SRC = '01020.png'

  def build_actions(self):
    event.Event.build_actions(self)

  def play(self):
    event.Event.play(self)
    self.game.insert_next_phase(ChooseUnrezzedIce(self.game, self.player, self))

  def is_playable(self):
    return event.Event.is_playable(self) and bool(self.unrezzed_ice())

  def force_rez_actions(self):
    return [ForceRezAction(self.game, self.player, card=ice)
            for ice in self.unrezzed_ice()]

  def unrezzed_ice(self):
    targets = []
    for server in self.game.corp.servers:
      for ice in server.ice.cards:
        if not ice.is_rezzed:
          targets.append(ice)
    return targets
