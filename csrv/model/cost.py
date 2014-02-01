"""Represents the cost of performing an action."""

from csrv.model import game_object


class Cost(game_object.PlayerObject):
  """Represents the cost to perform an action."""

  def __init__(self, game, player, card=None,
               credits=0, clicks=0,
               appropriations=None):
    game_object.PlayerObject.__init__(self, game, player)
    self.card = card
    self._credits = credits
    self._clicks = clicks
    self.appropriations = appropriations or []

  def clicks(self):
    return self._clicks

  def add_credits(self, num):
    self._credits += num

  def credits(self):
    return self._credits

  def can_pay(self, response=None, ignore_clicks=False):
    """Determine if the cost can be paid."""
    if (not ignore_clicks and
        self.player.clicks.value < self.clicks()):
      return False
    if self._available_credits() >= self.credits():
      return True
    return False

  def _available_credits(self):
    pools = self.player.find_pools(*self.appropriations)
    return sum([c.value for c in pools])

  def _pay_from_pools(self, credits):
    paid = 0
    pools = self.player.find_pools(*self.appropriations)
    sort_key = lambda p: p.utility()
    for pool in sorted(pools, key=sort_key):
      if not credits:
        break
      if pool.value >= credits:
        pool.lose(credits)
        credits = 0
        break
      else:
        credits -= pool.value
        pool.set(0)
    assert(not credits)

  def pay(self, response=None, ignore_clicks=False):
    """Pay the cost, possibly considering a response."""
    if not ignore_clicks:
      self.player.clicks.lose(self.clicks())
    self._pay_from_pools(self.credits())

  def __str__(self):
    costs = []
    if self.credits() == 1:
      costs.append('1 credit')
    elif self.credits():
      costs.append('%d credits' % self.credits())
    if self.clicks() == 1:
      costs.append('1 click')
    elif self.clicks():
      costs.append('%d clicks' % self.clicks())
    if not costs:
      costs.append('no cost')
    return '; '.join(costs)


class NullCost(Cost):
  """An empty cost."""

  def pay(self, response=None, **kwargs):
    pass

  def can_pay(self, response=None, **kwargs):
    return True


class OperationCost(Cost):

  def credits(self):
    return self.card.COST

  def clicks(self):
    return 1


class EventCost(Cost):

  def credits(self):
    return self.card.COST

  def clicks(self):
    return 1


class BasicActionCost(Cost):

  def clicks(self):
    return 1


class SimpleCost(Cost):
  pass


class RezAssetUpgradeCost(Cost):

  def credits(self):
    return self.card.COST


class RezIceCost(Cost):

  def credits(self):
    return self.card.cost


class PurgeVirusCountersCost(Cost):

  def clicks(self):
    return 3


class InstallAgendaAssetUpgradeCost(Cost):

  def clicks(self):
    return 1


class StealAgendaCost(Cost):

  def credits(self, response=None):
    return self.card.steal_cost


class InstallProgramCost(Cost):

  def clicks(self, response=None):
    return 1

  def credits(self, response=None):
    return self.card.cost


class InstallHardwareCost(Cost):

  def clicks(self, response=None):
    return 1

  def credits(self, response=None):
    return self.card.cost


class InstallResourceCost(Cost):

  def clicks(self, response=None):
    return 1

  def credits(self, response=None):
    return self.card.COST


class InstallIceCost(Cost):

  def credits(self, response=None):
    if response and response.server:
      credit_cost = response.server.ice.size
      return max((0, credit_cost - len(response.ice_to_trash)))
    return 0

  def can_pay(self, response=None, ignore_clicks=False):
    if (not ignore_clicks and
        self.player.clicks.value < self.clicks()):
      return False
    if self.player.credits.value >= self.credits(response):
      return True

  def pay(self, response=None, ignore_clicks=False):
    if not response:
      return Cost.pay(self, response, ignore_clicks=ignore_clicks)
    credits = self.credits(response)
    if not ignore_clicks:
      self.player.clicks.lose(self.clicks())
    self.player.credits.lose(credits)
    # TODO(mrroach): This is the wrong place for this. move to action.
    for card in response.ice_to_trash:
      response.server.uninstall_ice(card)

  def clicks(self):
    return 1


class AdvanceCardCost(Cost):

  def clicks(self):
    return 1

  def credits(self):
    return 1


class MakeARunCost(Cost):
  def clicks(self):
    return 1


class TrashOnAccessCost(Cost):

  def credits(self):
    return self.card.TRASH_COST
