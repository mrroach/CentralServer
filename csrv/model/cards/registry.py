class Registry(object):
  """A class to hold references to all known cards."""

  CARD_MAP = {}

  @classmethod
  def register(cls, card):
    cls.CARD_MAP[card.NAME] = card

  @classmethod
  def get(cls, name):
    return cls.CARD_MAP.get(name)
