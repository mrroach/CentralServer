from csrv.model import actions
from csrv.model import errors
from csrv.model import events
from csrv.model import modifiers
from csrv.model.cards import card_info
from csrv.model.cards import hardware


class InstallCard01040(actions.InstallHardware):

  def is_usable(self):
    if not actions.InstallHardware.is_usable(self):
      return False
    return bool(self.card.install_host_targets())

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if not response or not response.host:
      raise errors.InvalidResponse(
          'You must choose a host for Card01040')
    actions.InstallHardware.resolve(
        self, response, ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)


class Card01040(hardware.Hardware):

  NAME = u'Card01040'
  SET = card_info.CORE
  NUMBER = 40
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.MOD,
  ])
  COST = 2
  IMAGE_SRC = '01040.png'

  def __init__(self, game, player):
    hardware.Hardware.__init__(self, game, player)
    self.modifier = None

  def build_actions(self):
    hardware.Hardware.build_actions(self)
    self.install_action = InstallCard01040(self.game, self.player, self)

  def on_install(self):
    hardware.Hardware.on_install(self)
    self.modifier = modifiers.IcebreakerStrengthModifier(
        self.game, 1, card=self.host)

  def install_host_targets(self):
    targets = []
    for card in self.game.runner.rig.cards:
      if card_info.ICEBREAKER in card.KEYWORDS:
        targets.append(card)
    return targets

  def on_uninstall(self):
    hardware.Hardware.on_uninstall(self)
    if self.modifier:
      self.modifier.remove()
      self.modifier = None
