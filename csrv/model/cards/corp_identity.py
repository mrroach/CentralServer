from csrv.model import actions
from csrv.model.cards import card_base
from csrv.model import timing_phases


class CorpIdentity(card_base.CardBase):
  """A corp identity card."""

  TYPE = 'Identity'

  @property
  def starting_credit_pool(self):
    return 5

  @property
  def starting_hand_size(self):
    return 5

  @property
  def max_influence(self):
    return 15

  @property
  def minimum_deck_size(self):
    return 45
