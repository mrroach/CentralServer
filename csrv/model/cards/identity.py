"""An identity card."""

from csrv.model import actions
from csrv.model import game_object
from csrv.model.cards import card_base
from csrv.model import timing_phases
from csrv.model.cards import card_info


class Identity(card_base.CardBase):

  TYPE = card_info.IDENTITY
  START_CREDIT_POOL = 5
  START_HAND_SIZE = 5
  MAX_INFLUENCE = 15
  MIN_DECK_SIZE = 45

  @property
  def starting_credit_pool(self):
    return self.START_CREDIT_POOL

  @property
  def starting_hand_size(self):
    return self.START_HAND_SIZE

  @property
  def max_influence(self):
    return self.MAX_INFLUENCE

  @property
  def minimum_deck_size(self):
    return self.MAX_DECK_SIZE

class CorpIdentity(Identity):
  """A corp identity card."""

class RunnerIdentity(Identity):
  """A corp identity card."""
