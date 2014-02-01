from csrv.model import actions
from csrv.model import errors
from csrv.model.cards import agenda
from csrv.model.cards import card_info
from csrv.model.cards import ice
from csrv.model import timing_phases


class YesCard00055(actions.Action):
  DESCRIPTION = 'Perform beta test'


class NoCard00055(actions.Action):
  DESCRIPTION = 'No beta test'


class PerformCard00055(timing_phases.BasePhase):
  """Install ice from R&D, trash the rest."""

  def __init__(self, game, player):
    timing_phases.BasePhase.__init__(self, game, player)
    self.actions = {}

  def begin(self):
    if not self.begun:
      for i in range(3):
        if self.player.rnd.size:
          card = self.player.rnd.pop()
          if isinstance(card, ice.Ice):
            self.actions[card.install_action] = card
          else:
            card.trash()
    timing_phases.BasePhase.begin(self)

  def choices(self, refresh=False):
    if self._choices is None or refresh:
      self._choices = self.actions.keys()
    return self._choices

  def resolve(self, choice, response):
    if choice:
      choice.resolve(response, ignore_all_costs=True)
      self.actions[choice].rez()
      del self.actions[choice]
    if not choice or not self.choices(refresh=True):
      for card in self.actions.values():
        card.trash()
      self.end_phase()


class DecideCard00055(timing_phases.ActivateAbilityChoice):
  """Decide whether to look at three cards, install ice, trash the rest."""

  def __init__(self, game, player):
    timing_phases.ActivateAbilityChoice.__init__(
        self, game, player,
        YesCard00055(game, player),
        NoCard00055(game, player),
        PerformCard00055(game, player))


class Card00055(agenda.Agenda):

  NAME = 'Card00055'
  SUBTYPES = ['Research']
  COST = None
  FACTION = 'ROBOCORP'
  INFLUENCE = None
  NUMBER = 55
  SET = card_info.CORE
  IMAGE_SRC = '01055.png'
  AGENDA_POINTS = 2
  ADVANCEMENT_REQUIREMENT = 3

  def score(self):
    agenda.Agenda.score(self)
    self.game.insert_next_phase(DecideCard00055(self.game, self.player))

