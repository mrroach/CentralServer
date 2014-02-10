from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import operation


class ChooseCardsToAdvance(timing_phases.BasePhase):
  """Choose up to 2 advanceable cards."""

  def __init__(self, game, player, card):
    timing_phases.BasePhase.__init__(self, game, player, both_players=False)
    self.card = card
    self.already_advanced = set()

  def choices(self, refresh=False):
    if not self._choices or refresh:
      self._choices = [a for a in self.card.place_advancement_actions()
                       if not a.card in self.already_advanced]
    return self._choices

  def resolve(self, choice, response=None):
    timing_phases.BasePhase.resolve(self, choice, response)
    if choice:
      self.already_advanced.add(choice.card)
    if not choice or len(self.already_advanced) > 1:
      self.end_phase()


class Card01100(operation.Operation):

  NAME = u'Card01100'
  SET = card_info.CORE
  NUMBER = 100
  SIDE = card_info.CORP
  FACTION = card_info.MEATCORP
  INFLUENCE = 1
  UNIQUE = False
  COST = 0
  IMAGE_SRC = '01100.png'

  def build_actions(self):
    operation.Operation.build_actions(self)

  def play(self):
    operation.Operation.play(self)
    self.game.insert_next_phase(
        ChooseCardsToAdvance(self.game, self.player, self))

  def is_playable(self):
    return (operation.Operation.is_playable(self) and
            bool(self.advanceable_cards()))

  def advanceable_cards(self):
    targets = []
    for server in self.game.corp.servers:
      for card in server.ice.cards + server.installed.cards:
        if card.can_be_advanced():
          targets.append(card)
    return targets

  def place_advancement_actions(self):
    return [actions.PlaceAdvancement(self.game, self.player, card)
            for card in self.advanceable_cards()]
