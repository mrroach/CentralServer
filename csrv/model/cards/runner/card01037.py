from csrv.model import actions
from csrv.model import events
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import event


class ChooseIce(timing_phases.BasePhase):
  """Choose a piece of ice for card01037."""

  def __init__(self, game, player):
    timing_phases.BasePhase.__init__(self, game, player, both_players=False)

  def resolve(self, choice, response):
    timing_phases.BasePhase.resolve(self, choice, response)
    if choice:
      self.end_phase()


class Card01037Action(actions.Action):

  def __init__(self, game, player, card=None, card01037=None):
    actions.Action.__init__(self, game, player, card=card)
    self.card01037 = card01037

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.Action.resolve(
        self, response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.card01037.modify(self.card)

  @property
  def description(self):
    if self.card.is_faceup:
      return 'Add sentry, code gate, and barrier to %s' % self.card
    else:
      return 'Add sentry, code gate, and barrier to ice'


class Card01037(event.Event):

  NAME = u'Card01037'
  SET = card_info.CORE
  NUMBER = 37
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 4
  UNIQUE = False
  KEYWORDS = set([
      card_info.MOD,
  ])
  COST = 0
  IMAGE_SRC = '01037.png'

  def __init__(self, game, player):
    event.Event.__init__(self, game, player)
    self.ice = None
    self.added = None

  def build_actions(self):
    event.Event.build_actions(self)

  def play(self):
    event.Event.play(self)
    self.game.register_choice_provider(ChooseIce, self, 'modify_ice_actions')
    self.game.insert_next_phase(ChooseIce(self.game, self.player))

  def is_playable(self):
    return event.Event.is_playable(self) and bool(self.modify_ice_actions())

  def modify(self, ice):
    self.game.deregister_choice_provider(ChooseIce, self, 'modify_ice_actions')
    self.game.register_listener(events.RunnerTurnEnd, self)
    self.ice = ice
    types = set([card_info.BARRIER, card_info.SENTRY, card_info.CODE_GATE])
    to_add = types - self.ice.KEYWORDS
    self.ice.KEYWORDS.update(to_add)
    self.added = to_add

  def on_runner_turn_end(self, sender, event):
    self.game.deregister_listener(events.RunnerTurnEnd, self)
    if self.ice:
      self.ice.KEYWORDS.difference_update(self.added)
      self.ice = None
      self.added = None

  def modify_ice_actions(self):
    actions = []
    for server in self.game.corp.servers:
      for ice in server.ice.cards:
        actions.append(Card01037Action(
            self.game, self.player, card=ice,
            card01037=self))
    return actions

