class DrawFromEmptyServer(Exception):
  """Attempted to draw from an empty R&D (corp loses)."""


class ChoiceRequiredError(Exception):
  """A choice is required for."""


class InvalidPaymentChoice(Exception):
  """An invalid payment choice has been made."""


class CostNotSatisfied(Exception):
  """Required costs are not met."""


class InsufficientFunds(Exception):
  """Attempt to draw more out of a resource pool than exists."""


class InvalidResponse(Exception):
  """The response sent by the client is invalid."""
