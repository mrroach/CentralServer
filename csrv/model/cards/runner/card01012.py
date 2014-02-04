from csrv.model import actions
from csrv.model import errors
from csrv.model import events
from csrv.model import modifiers
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import ice
from csrv.model.cards import program


class InstallCard01012(actions.InstallProgram):

  def is_usable(self):
    if not actions.InstallProgram.is_usable(self):
      return False
    for server in self.game.corp.servers:
      for card in server.ice.cards:
        if card.is_rezzed:
          return True

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if not response or not response.host:
      raise errors.InvalidResponseError(
          'You must choose a host for Card01012.')
    actions.InstallProgram.resolve(
        self, response, ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)


class Card01012(program.Program):

  NAME = u'Card01012'
  SET = card_info.CORE
  NUMBER = 12
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.VIRUS,
  ])
  COST = 2
  MEMORY = 1
  IMAGE_SRC = '01012.png'

  WHEN_INSTALLED_LISTENS = [
      events.RunnerTurnBegin,
      events.IceStrengthChanged,
  ]

  def __init__(self, game, player, location=None):
    program.Program.__init__(self, game, player, location)
    self.modifier = None

  def install_host_targets(self):
    targets = []
    for server in self.game.corp.servers:
      for card in server.ice.cards:
        if card.is_rezzed:
          targets.append(card)
    return targets

  def get_virus_counters(self):
    return self._virus_counters

  def set_virus_counters(self, value):
    self._virus_counters = value
    if not self.modifier:
      self.modifier = modifiers.IceStrengthModifier(
          self.game, 0, card=self.host)
    self.modifier.set_value(-1 * self._virus_counters)

  virus_counters = property(get_virus_counters, set_virus_counters)

  def on_ice_strength_changed(self, sender, event):
    if self.host.strength <= 0:
      self.host.trash()

  def build_actions(self):
    program.Program.build_actions(self)
    self.install_action = InstallCard01012(
        self.game, self.player, self)

  def on_runner_turn_begin(self, sender, event):
    self.virus_counters += 1

  def on_uninstall(self):
    program.Program.on_uninstall(self)
    if self.modifier:
      self.modifier.remove()
      self.modifier = None
