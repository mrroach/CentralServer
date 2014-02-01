"""An identity card."""

from csrv.model import actions
from csrv.model import game_object
from csrv.model.cards import card_base
from csrv.model import timing_phases


class Identity(card_base.CardBase):

  TYPE = 'Identity'

