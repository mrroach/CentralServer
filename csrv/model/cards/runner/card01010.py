from csrv.model.cards import card_info
from csrv.model.cards import program
from csrv.model import actions
from csrv.model import errors
from csrv.model import events
from csrv.model import modifiers
from csrv.model import parameters
from csrv.model import timing_phases


class ChooseNumCardsAction(actions.Action):
  DESCRIPTION = 'Choose how many extra cards to access from R&D'
  REQUEST_CLASS = parameters.NumericChoiceRequest

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if (not response or response.number < 0 or response.number >
        self.card.virus_counters - 1):
      raise errors.InvalidResponse(
          'You must select a number between 0 and %d' %
          (self.card.virus_counters - 1))
    self.card.choose_num_cards(response.number)
    actions.Action.resolve(
        self, response, ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)


class Card01010(program.Program):

  NAME = u'Card01010'
  SET = card_info.CORE
  NUMBER = 10
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 3
  UNIQUE = False
  KEYWORDS = set([
      card_info.VIRUS,
  ])
  COST = 3
  MEMORY = 1
  IMAGE_SRC = '01010.png'

  WHEN_INSTALLED_LISTENS = [
      events.BeginApproachServer_4_5,
  ]

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.ChooseNumCardsToAccess: 'choose_num_cards_actions',
  }

  def build_actions(self):
    program.Program.build_actions(self)
    self._choose_num_cards_action = ChooseNumCardsAction(
        self.game, self.player, self)

  def choose_num_cards_actions(self):
    return [self._choose_num_cards_action]

  def on_begin_approach_server_4_5(self, sender, event):
    if self.game.run and self.game.run.server == self.game.corp.rnd:
      self.virus_counters += 1
      if self.virus_counters > 1:
        # TODO(mrroach): set a default value
        phase = timing_phases.ChooseNumCardsToAccess(self.game, self.player)
        self.game.insert_next_phase(phase)
        phase.begin()

  def choose_num_cards(self, number):
    if number:
      modifiers.NumRndCardsToAccess(
          self.game, number,
          server=self.game.corp.rnd,
          until=events.EndApproachServer_4_5)
