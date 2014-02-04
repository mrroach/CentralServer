"""Common player implementation."""

from csrv.model import actions
from csrv.model import events
from csrv.model import timing_phases
from csrv.model import game_object
from csrv.model import locations
from csrv.model import modifiers
from csrv.model import pool


class Player(game_object.GameObject):
  """Common player implementation."""

  def __init__(self, game, deck):
    game_object.GameObject.__init__(self, game)
    self.deck = deck
    self.identity = deck.identity(game, self)
    self.agenda_points = 0
    self.credits = pool.MainCreditPool(game, self, 0)
    self.credit_pools = set()
    self.clicks = pool.ClickPool(game, self, 0)

  def find_pools(self, *appropriations):
    # This is going to have to take into account "in this server" stuff.
    appropriations = set(appropriations)
    pools = [self.credits]
    if appropriations:
      for pool in self.credit_pools:
        if (not pool.appropriation) or (pool.appropriation & appropriations):
          pools.append(pool)
    else:
      for pool in self.credit_pools:
        if not pool.appropriation:
          pools.append(pool)
    return pools

  def trash(self, card):
    if card.host:
      card.host.unhost_card(card)
    for hosted in list(card.hosted_cards):
      hosted.trash()
    if card.location and card.location.parent:
      card.location.parent.remove(card)
    elif card.location:
      card.location.remove(card)


class RunnerPlayer(Player):

  LISTENS = [
      events.BeginRunnerGameSetup,
      events.BeginRunnerTurnBegin,
  ]

  PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerGameSetup: 'runner_game_setup_actions',
      timing_phases.RunnerTurnActions: 'runner_turn_actions',
  }

  def __init__(self, game, deck):
    Player.__init__(self, game, deck)
    self.link = pool.Pool(game, self, self.identity.BASE_LINK)
    self.tags = 0
    self.stack = locations.Stack(game, self)
    self.heap = locations.Heap(game, self)
    self.grip = locations.Grip(game, self)
    self.rig = locations.Rig(game, self)
    self.mulligan_used = False
    self.installed_cards = set()
    self.scored_agendas = locations.RunnerScoreArea(game, self)
    self.basic_actions = [
        actions.DrawFromStack(self.game, self),
        actions.GainACredit(self.game, self),
        actions.RemoveATag(self.game, self),
    ]
    self._brain_damage = 0
    self._brain_damage_modifier = None

    for card in self.deck.cards:
      self.stack.add(card(self.game, self))

  def __str__(self):
    return 'runner'

  # The order in which the event fires doesn't work right for this
  def on_begin_runner_game_setup(self, event, sender):
    self.draw_starting_hand_and_credits(mulligan=False)

  def draw_starting_hand_and_credits(self, mulligan=True):
    if mulligan:
      self.game.log('The runner takes a mulligan')
    self.mulligan_used = mulligan
    self.credits.set(5) #self.deck.identity.starting_credit_pool)
    self.stack.shuffle()
    for card in list(self.grip.cards):
      self.grip.remove(card)
      self.stack.add(card)
      self.stack.shuffle()
    for i in range(self.starting_hand_size):
      self.grip.add(self.stack.pop())

  def runner_game_setup_actions(self):
    """Return the actions that can be taken during this phase."""
    if self.mulligan_used:
      return []
    else:
      return [actions.MulliganAction(self.game, self)]

  def runner_turn_actions(self):
    return self.basic_actions

  def on_begin_runner_turn_begin(self, sender, event):
    self.clicks.gain(4)

  def trash(self, card):
    Player.trash(self, card)
    self.heap.add(card)

  def take_damage(self, dmg):
    starting_grip_size = self.grip.size
    for i in range(min(dmg, starting_grip_size)):
      self.grip.pick().trash()
    if starting_grip_size < dmg:
      self.game.runner_flatline()

  @property
  def free_memory(self):
    used = 0
    for card in self.rig.cards:
      if card.host:
        used += card.host.hosted_card_memory(card)
      else:
        used += card.memory
    return self.memory - used

  @property
  @modifiers.modifiable(modifiers.MemorySize,
                        card_scope=False, server_scope=False)
  def memory(self):
    return 4

  @property
  @modifiers.modifiable(modifiers.RunnerMaxHandSize,
                        card_scope=False, server_scope=False)
  def max_hand_size(self):
    return 5

  @property
  @modifiers.modifiable(modifiers.RunnerStartingHandSize,
                        card_scope=False, server_scope=False)
  def starting_hand_size(self):
    return 5

  def get_brain_damage(self):
    return self._brain_damage

  def set_brain_damage(self, value):
    self._brain_damage = value
    if not self._brain_damage_modifier:
      self._brain_damage_modifier = modifiers.RunnerMaxHandSize(self.game, 0)
    self._brain_damage_modifier.increase(-1 * value)
  brain_damage = property(get_brain_damage, set_brain_damage)


class CorpPlayer(Player):

  LISTENS = [
      events.BeginCorpGameSetup,
      events.CorpTurnBegin,
  ]

  PROVIDES_CHOICES_FOR = {
      timing_phases.CorpGameSetup: 'corp_game_setup_actions',
      timing_phases.CorpTurnActions: 'corp_turn_actions',
  }

  def __init__(self, game, deck):
    Player.__init__(self, game, deck)
    self._bad_publicity = 0
    self.rnd = locations.RnD(game, self)
    self.archives = locations.Archives(game, self)
    self.hq = locations.HQ(game, self)
    self.centrals = set([self.rnd, self.archives, self.hq])
    self.mulligan_used = False
    self.remotes = []
    self.installed_cards = set()
    self.rezzed_cards = set()
    self.installed_ice = set()
    self.rezzed_ice = set()
    self.scored_agendas = locations.CorpScoreArea(game, self)
    self.basic_actions = [
        actions.DrawFromRnD(self.game, self),
        actions.GainACredit(self.game, self),
        actions.PurgeVirusCounters(self.game, self)
    ]
    for card in self.deck.cards:
      self.rnd.add(card(self.game, self))

  def __str__(self):
    return 'corp'

  @property
  def servers(self):
    return [self.rnd, self.archives, self.hq] + self.remotes

  def on_begin_corp_game_setup(self, event, sender):
    self.draw_starting_hand_and_credits(mulligan=False)

  def draw_starting_hand_and_credits(self, mulligan=True):
    if mulligan:
      self.game.log('The corp takes a mulligan')
    self.mulligan_used = mulligan
    self.rnd.shuffle()
    self.credits.set(5)
    for card in list(self.hq.cards):
      self.hq.remove(card)
      self.rnd.add(card)
      self.rnd.shuffle()
    for i in range(self.starting_hand_size):
      self.hq.add(self.rnd.pop())

  def corp_game_setup_actions(self):
    """Return the actions that can be taken during this phase."""
    if self.mulligan_used:
      return []
    else:
      return [actions.MulliganAction(self.game, self)]

  def corp_turn_actions(self):
    return self.basic_actions

  def on_corp_turn_begin(self, sender, event):
    self.clicks.gain(3)
    self.hq.add(self.rnd.pop())

  def new_remote_server(self):
    remote = locations.RemoteServer(self.game, self, len(self.remotes))
    self.remotes.append(remote)
    return remote

  def remove_remote_server(self, server):
    self.remotes.remove(server)
    if self.game.run and self.game.run.server == server:
      self.game.run.cancel()

  def trash(self, card):
    Player.trash(self, card)
    self.archives.add(card)

  @property
  @modifiers.modifiable(modifiers.CorpMaxHandSize,
                        card_scope=False, server_scope=False)
  def max_hand_size(self):
    return 5

  @property
  @modifiers.modifiable(modifiers.CorpStartingHandSize,
                        card_scope=False, server_scope=False)
  def starting_hand_size(self):
    return 5

  def get_bad_publicity(self):
    return self._bad_publicity

  def set_bad_publicity(self, value):
    self._bad_publicity = value

  bad_publicity = property(get_bad_publicity, set_bad_publicity)

