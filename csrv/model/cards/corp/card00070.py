from csrv.model import actions
from csrv.model import cost
from csrv.model import timing_phases
from csrv.model.cards import asset
from csrv.model.cards import card_info


class YesCard00070(actions.Action):
  DESCRIPTION = 'Pay 4 [credits], do 3 net damage and give the runner 1 tag'

  def __init__(self, game, player):
    cost_obj = cost.Cost(game, player, credits=4)
    actions.Action.__init__(self, game, player, cost=cost_obj)

  def resolve(self, response=None):
    actions.Action.resolve(self, response=response)
    self.game.log('The runner takes 3 net damage and a tag.')
    self.game.runner.tags += 1
    damage_phase = timing_phases.TakeNetDamage(self.game, self.game.runner, 3)
    self.game.insert_next_phase(damage_phase)


class NoCard00070(actions.Action):
  DESCRIPTION = 'Do not activate Card00070!'


class DecideCard00070(timing_phases.ActivateAbilityChoice):
  """Choose whether to activate Card00070!"""

  def __init__(self, game, player):
    timing_phases.ActivateAbilityChoice.__init__(
        self, game, player,
        YesCard00070(game, player),
        NoCard00070(game, player),
        None)


class Card00070(asset.Asset):

  NAME = u'Card00070!'
  SET = card_info.CORE
  NUMBER = 70
  SIDE = card_info.CORP
  FACTION = card_info.NETCORP
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.AMBUSH,
  ])
  COST = 0
  IMAGE_SRC = '01070.png'
  TRASH_COST = 0

  def build_actions(self):
    asset.Asset.build_actions(self)

  def on_access(self):
    if self.location.parent == self.game.corp.archives:
      return
    self.log('The runner accessed Card00070!')
    if self.location.parent == self.game.corp.rnd:
      self.game.expose_card(self)
    phase = DecideCard00070(self.game, self.player)
    self.game.insert_next_phase(phase)
    phase.begin()
    asset.Asset.on_access(self)
