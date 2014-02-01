"""Break a code gate subroutine."""

from csrv.model.actions import break_subroutine
from csrv.model.cards import card_info


class BreakCodeGateSubroutine(break_subroutine.BreakSubroutine):

  DESCRIPTION = 'Break a code gate subroutine'
  REQUIRED_KEYWORDS = set([card_info.CODE_GATE])
