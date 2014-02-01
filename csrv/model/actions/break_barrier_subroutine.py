"""Break a barrier subroutine."""

from csrv.model.actions import break_subroutine
from csrv.model.cards import card_info


class BreakBarrierSubroutine(break_subroutine.BreakSubroutine):

  DESCRIPTION = 'Break a barrier subroutine'
  REQUIRED_KEYWORDS = set([card_info.BARRIER])
