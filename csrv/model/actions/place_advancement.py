from csrv.model import cost
from csrv.model.actions import advance_card


class PlaceAdvancement(advance_card.AdvanceCard):

  DESCRIPTION = "Place an advancement token via some card effect."
  COST_CLASS = cost.NullCost

  @property
  def description(self):
    return "Place an advancement token on %s" % self.card
