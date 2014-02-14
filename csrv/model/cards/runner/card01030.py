from csrv.model import actions
from csrv.model import appropriations
from csrv.model import pool
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import resource


class PreventMeatDamage(actions.Action):
  DESCRIPTION = 'Prevent up to 3 meat damage'

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.Action.resolve(
        self, response=response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    damage = self.game.current_phase().damage
    self.game.current_phase().damage = max(0, damage - 3)
    self.card.trash()


class Card01030(resource.Resource):

  NAME = u'Card01030'
  SET = card_info.CORE
  NUMBER = 30
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.LOCATION,
  ])
  COST = 2
  IMAGE_SRC = '01030.png'

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.TakeMeatDamage: 'prevent_meat_damage_actions',
  }

  def __init__(self, game, player):
    resource.Resource.__init__(self, game, player)
    self.pool = None

  def build_actions(self):
    resource.Resource.build_actions(self)
    self._prevent_meat_damage = PreventMeatDamage(self.game, self.player, self)

  def prevent_meat_damage_actions(self):
    return [self._prevent_meat_damage]

  @property
  def credits(self):
    if self.pool:
      return self.pool.value
    return 0

  def on_install(self):
    resource.Resource.on_install(self)
    self.pool = pool.CreditPool(
        self.game, self.player, 2,
        appropriation=set([appropriations.REMOVE_TAGS]),
        recurring=True)
    self.player.credit_pools.add(self.pool)

  def on_uninstall(self):
    self.pool.remove()
    self.player.credit_pools.remove(self.pool)
    self.pool = None
