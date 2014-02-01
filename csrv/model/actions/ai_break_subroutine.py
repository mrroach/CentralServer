"""Break a subroutine with AI."""

from csrv.model.actions import break_subroutine
from csrv.model.cards import card_info


class AiBreakSubroutine(break_subroutine.BreakSubroutine):

  DESCRIPTION = 'Break a subroutine with ai'

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    break_subroutine.BreakSubroutine.resolve(self, response)
    self.card.on_used_to_break_subroutine()
