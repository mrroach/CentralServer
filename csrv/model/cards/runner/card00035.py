from csrv.model import modifiers
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import event


class InstallWithDiscount(timing_phases.BasePhase):
  """Install a program or piece of hardware, lowering cost by 3."""

  NULL_OK = False
  DESCRIPTION = 'Install a program or piece of hardware, lowering cost by 3.'

  def __init__(self, game, player):
    timing_phases.BasePhase.__init__(self, game, player, both_players=False)

  def begin(self):
    timing_phases.BasePhase.begin(self)
    self._modifiers = [
        modifiers.ProgramCostModifier(self.game, -3),
        modifiers.HardwareCostModifier(self.game, -3),
    ]

  def choices(self, refresh=False):
    if not self._choices or refresh:
      self._choices = []
      for card in self.player.grip.cards:
        if card.TYPE in ['Program', 'Hardware']:
          self._choices.append(card.install_action)
    return self._choices

  def resolve(self, choice, response=None):
    choice.resolve(response=response, ignore_clicks=True)
    if choice:
      self.end_phase()

  def end_phase(self):
    timing_phases.BasePhase.end_phase(self)
    for modifier in self._modifiers:
      modifier.remove()


class Card00035(event.Event):

  NAME = u'Card00035'
  SET = card_info.CORE
  NUMBER = 35
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.MOD,
  ])
  COST = 0
  IMAGE_SRC = '01035.png'

  def build_actions(self):
    event.Event.build_actions(self)

  def is_playable(self):
    have_installable = False
    for card in self.player.grip.cards:
      if (card.TYPE in ['Program', 'Hardware'] and
          card.cost - 3 < self.player.credits.value):
        have_installable = True
        break
    return have_installable and event.Event.is_playable(self)

  def play(self):
    event.Event.play(self)
    self.game.insert_next_phase(InstallWithDiscount(self.game, self.player))
