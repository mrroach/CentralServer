"""Basic implementation of a card."""

from csrv.model import game_object
from csrv.model import events
from csrv.model.cards import registry
from csrv.model.cards import card_info

class CardMeta(type):
  """A metaclass to register every known card."""

  def __new__(mcs, name, bases, new_attrs):
    for attr, values in new_attrs.items():
      if attr.startswith('WHEN_') and attr.endswith('_LISTENS'):
        for parent_class in bases:
          parent_values = getattr(parent_class, attr, [])
          for parent_value in parent_values:
            if parent_value not in values:
              values.append(parent_value)
      if attr.startswith('WHEN_') and attr.endswith('_CHOICES_FOR'):
        for parent_class in bases:
          parent_values = getattr(parent_class, attr, {})
          for parent_key in parent_values:
            if parent_key not in values:
              values[parent_key] = parent_values[parent_key]

    klass = type.__new__(mcs, name, bases, new_attrs)
    if 'NAME' in new_attrs:
      registry.Registry.register(klass)
    return klass


class CardBase(game_object.PlayerObject):

  __metaclass__ = CardMeta

  ADVANCEMENT_REQUIREMENT = None
  AGENDA_POINTS = 0
  COST = 0
  FACTION = None
  INFLUENCE = 0
  KEYWORDS = set()
  MEMORY = 0
  NAME = None
  REZZABLE = False
  STRENGTH = 0
  TYPE = card_info.UNKNOWN

  # Which timing phases this card provides choices for
  # based on the state/location of the card at the time
  WHEN_ACCESSED_PROVIDES_CHOICES_FOR = {}
  WHEN_BANISHED_PROVIDES_CHOICES_FOR = {}
  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {}
  WHEN_IN_ARCHIVES_PROVIDES_CHOICES_FOR = {}
  WHEN_IN_CORP_SCORE_AREA_PROVIDES_CHOICES_FOR = {}
  WHEN_IN_HAND_PROVIDES_CHOICES_FOR = {}
  WHEN_IN_HEAP_PROVIDES_CHOICES_FOR = {}
  WHEN_IN_RND_PROVIDES_CHOICES_FOR = {}
  WHEN_IN_RUNNER_SCORE_AREA_PROVIDES_CHOICES_FOR = {}
  WHEN_IN_STACK_PROVIDES_CHOICES_FOR = {}
  WHEN_REZZED_PROVIDES_CHOICES_FOR = {}

  # It probably makes sense to get rid of this entirely
  # and just make everything use a timing phase
  WHEN_ACCESSED_LISTENS = []
  WHEN_BANISHED_LISTENS = []
  WHEN_INSTALLED_LISTENS = []
  WHEN_IN_ARCHIVES_LISTENS = []
  WHEN_IN_CORP_SCORE_AREA_LISTENS = []
  WHEN_IN_HAND_LISTENS = []
  WHEN_IN_HEAP_LISTENS = []
  WHEN_IN_RND_LISTENS = []
  WHEN_IN_RUNNER_SCORE_AREA_LISTENS = []
  WHEN_IN_STACK_LISTENS = []
  WHEN_REZZED_LISTENS = []

  def __init__(self, game, player, location=None):
    game_object.PlayerObject.__init__(self, game, player)
    self.location = location
    self.is_faceup = False
    self.is_rezzed = False
    self.is_installed = False
    self.is_in_hand = False
    self.is_being_accessed = False
    self._advancement_tokens = 0
    self._virus_counters = 0
    self._agenda_counters = 0
    self._power_counters = 0
    self.host = None
    self.hosted_cards = set()

    self.set_new_id()
    self.build_actions()

  def __str__(self):
    return self.NAME

  @property
  def server(self):
    if self.host:
      return self.host.server
    if self.location:
      if self.location.parent:
        return self.location.parent
      else:
        return self.location

  def get_virus_counters(self):
    return self._virus_counters

  def set_virus_counters(self, value):
    self._virus_counters = value

  virus_counters = property(get_virus_counters, set_virus_counters)

  def get_advancement_tokens(self):
    return self._advancement_tokens

  def set_advancement_tokens(self, value):
    self._advancement_tokens = value

  advancement_tokens = property(get_advancement_tokens, set_advancement_tokens)

  def get_agenda_counters(self):
    return self._agenda_counters

  def set_agenda_counters(self, value):
    self._agenda_counters = value

  agenda_counters = property(get_agenda_counters, set_agenda_counters)

  @property
  def agenda_points(self):
    return self.AGENDA_POINTS

  def get_power_counters(self):
    return self._power_counters

  def set_power_counters(self, value):
    self._power_counters = value

  power_counters = property(get_power_counters, set_power_counters)

  @property
  def credits(self):
    """How many credits are hosted on this card."""
    return 0

  def build_actions(self):
    """Create action objects."""

  def can_host(self, card):
    """Can this card host the given card."""
    return False

  def meets_memory_limits(self, card):
    """Will hosting this card stay within memory limits for host."""
    return True

  def host_card(self, card):
    """Host the given card on this card."""
    card.host = self
    self.hosted_cards.add(card)

  def unhost_card(self, card):
    self.hosted_cards.remove(card)
    card.host = None

  def hosted_card_memory(self, card):
    """Return an adjusted memory value for a card that is hosted on this one."""
    return card.memory

  @property
  def memory(self):
    return self.MEMORY

  @property
  def cost(self):
    return self.COST

  @property
  def strength(self):
    return self.STRENGTH

  @property
  def can_rez(self):
    return self.REZZABLE and self.is_installed and not self.is_rezzed

  @property
  def rez_cost(self):
    return self.COST

  @property
  def is_exposed(self):
    return self.game_id in self.game.exposed_ids

  def advance(self):
    self.advancement_tokens += 1

  @property
  def is_advanceable(self):
    return getattr(self, 'ADVANCEABLE', False)

  def can_be_advanced(self):
    return self.is_installed and self.is_advanceable

  def rez(self):
    self.is_rezzed = True
    self.is_faceup = True
    self.on_rez()

  def derez(self):
    self.is_rezzed = False
    self.is_faceup = False
    self.on_derez()

  @classmethod
  def influence_cost(cls, faction):
    """Card influence cost for a given faction"""
    if cls.FACTION == faction or cls.FACTION == card_info.NEUTRAL:
      return 0
    else:
      return cls.INFLUENCE

  def forfeit_agenda_targets(self):
    """Agendas that may be forfeited."""
    return list(self.player.scored_agendas.cards)

  def _setup_choices(self, state):
    for timing_phase, method in getattr(
        self, 'WHEN_%s_PROVIDES_CHOICES_FOR' % state).iteritems():
      self.game.register_choice_provider(timing_phase, self, method)
    for event in getattr(self, 'WHEN_%s_LISTENS' % state):
      self.game.register_listener(event, self)
    setattr(self, 'is_%s' % state.lower(), True)

  def _teardown_choices(self, state):
    for timing_phase, method in getattr(
        self, 'WHEN_%s_PROVIDES_CHOICES_FOR' % state).iteritems():
      self.game.deregister_choice_provider(timing_phase, self, method)
    for event in getattr(self, 'WHEN_%s_LISTENS' % state):
      self.game.deregister_listener(event, self)
    setattr(self, 'is_%s' % state.lower(), False)

  def on_rez(self):
    self._setup_choices('REZZED')

  def on_derez(self):
    self._teardown_choices('REZZED')

  def on_enter_hand(self):
    self.is_faceup = False
    self._setup_choices('IN_HAND')
    self.set_new_id()

  def on_exit_hand(self):
    self._teardown_choices('IN_HAND')
    self.set_new_id()

  def on_enter_heap(self):
    self._setup_choices('IN_HEAP')
    self.set_new_id()

  def on_exit_heap(self):
    self._teardown_choices('IN_HEAP')
    self.set_new_id()

  def on_enter_stack(self):
    self.is_faceup = False
    self._setup_choices('IN_STACK')

  def on_exit_stack(self):
    self._teardown_choices('IN_STACK')
    self.set_new_id()

  def on_enter_archives(self):
    # We leave faceup in its current state
    self.is_rezzed = False
    self._setup_choices('IN_ARCHIVES')
    self.set_new_id()

  def on_exit_archives(self):
    self._teardown_choices('IN_ARCHIVES')
    self.set_new_id()

  def on_enter_rnd(self):
    self.is_faceup = False
    self._setup_choices('IN_RND')

  def on_exit_rnd(self):
    self._teardown_choices('IN_RND')

  def on_enter_corp_score_area(self):
    self.is_faceup = True
    self._setup_choices('IN_CORP_SCORE_AREA')
    self.set_new_id()

  def on_exit_corp_score_area(self):
    self._teardown_choices('IN_CORP_SCORE_AREA')

  def on_enter_runner_score_area(self):
    self.is_faceup = True
    self._setup_choices('IN_RUNNER_SCORE_AREA')
    self.game.runner.agenda_points += self.agenda_points

  def on_exit_runner_score_area(self):
    self._teardown_choices('IN_RUNNER_SCORE_AREA')
    self.game.runner.agenda_points -= self.agenda_points

  def on_banish(self):
    self._setup_choices('BANISHED')

  def on_install(self):
    self._setup_choices('INSTALLED')

  def on_uninstall(self):
    self.trigger_event(events.UninstallCard(self.game, self.player))
    self._teardown_choices('INSTALLED')

  def on_access(self):
    self.is_being_accessed = True
    self._setup_choices('ACCESSED')

  def on_access_end(self):
    self.is_being_accessed = False
    self._teardown_choices('ACCESSED')

  def banish(self):
    self.location.parent.remove(self)
    self.game.banished.add(self)

  def trash(self):
    self.player.trash(self)
