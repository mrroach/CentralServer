from csrv.model import actions
from csrv.model import errors
from csrv.model import parameters
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import operation
from csrv.model.cards import agenda
from csrv.model.cards import asset
from csrv.model.cards import ice
from csrv.model.cards import upgrade


class Card00060Phase(timing_phases.BasePhase):
  """Install cards (spending no clicks but paying all install costs."""

  def __init__(self, game, player):
    timing_phases.BasePhase.__init__(self, game, player)
    self._installed = 0

  def choices(self, refresh=False):
    if (self._choices is None or refresh):
      installable = (agenda.Agenda, asset.Asset, ice.Ice, upgrade.Upgrade)
      installable_cards = [card for card in self.player.hq.cards
                           if isinstance(card, installable)]
      self._choices = [card.install_action for card in installable_cards]
    return self._choices

  def resolve(self, choice, response=None):
    if choice:
      choice.resolve(response, ignore_clicks=True)
      self._installed += 1
    if not self.choices(refresh=True) or not choice or self._installed >= 3:
      self.end_phase()


class Card00060(operation.Operation):

  NAME = u'Card00060'
  SET = card_info.CORE
  NUMBER = 60
  SIDE = card_info.CORP
  FACTION = card_info.ROBOCORP
  INFLUENCE = 2
  UNIQUE = False
  COST = 1
  IMAGE_SRC = '01060.png'

  def build_actions(self):
    operation.Operation.build_actions(self)

  def play(self):
    self.game.insert_next_phase(
        Card00060Phase(self.game, self.player))

