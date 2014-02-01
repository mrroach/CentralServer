"""Break a sentry subroutine."""

from csrv.model.actions import break_subroutine
from csrv.model.cards import card_info


class BreakSentrySubroutine(break_subroutine.BreakSubroutine):

  DESCRIPTION = 'Break a sentry subroutine'
  REQUIRED_KEYWORDS = set([card_info.SENTRY])
