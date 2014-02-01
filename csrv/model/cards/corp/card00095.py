from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import agenda
from csrv.model.cards import card_info


class YesCard00095(actions.Action):
  DESCRIPTION = ('Forfeit Card00095 to give the Runner 1 tag and'
                 ' take 1 bad publicity')


class NoCard00095(actions.Action):
  DESCRIPTION = 'Do not forfeit Card00095'


class DecideCard00095(timing_phases.ActivateAbilityChoice):
  """Decide whether to forfeit Card00095 to give a tag."""
  NULL_OK = False

  def __init__(self, game, player, card):
    timing_phases.ActivateAbilityChoice.__init__(
        self, game, player,
        YesCard00095,
        NoCard00095,
        None)
    self.card = card

  def resolve(self, choice, response=None):
    if choice == self.yes_action:
      self.card.banish()
      self.game.corp.bad_publicity += 1
      self.game.runner.tags += 1
    self.end_phase()


class Card00095(agenda.Agenda):

  NAME = u'Card00095'
  SET = card_info.CORE
  NUMBER = 95
  SIDE = card_info.CORP
  FACTION = card_info.MEATCORP
  UNIQUE = False
  KEYWORDS = set([
      card_info.SECURITY,
  ])
  ADVANCEMENT_REQUIREMENT = 3
  AGENDA_POINTS = 1
  IMAGE_SRC = '01095.png'

  def build_actions(self):
    agenda.Agenda.build_actions(self)

  def score(self):
    agenda.Agenda.score(self)
    self.game.insert_next_phase(DecideCard00095(self.game, self.player))
