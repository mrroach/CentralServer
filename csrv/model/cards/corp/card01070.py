from csrv.model import actions
from csrv.model import cost
from csrv.model import timing_phases
from csrv.model.cards import asset
from csrv.model.cards import card_info


class YesCard01070(actions.Action):
  DESCRIPTION = 'Pay 4 [credits], do 3 net damage and give the runner 1 tag'

  def __init__(self, game, player):
    cost_obj = cost.Cost(game, player, credits=4)
    actions.Action.__init__(self, game, player, cost=cost_obj)

  def resolve(self, response=None):
    actions.Action.resolve(self, response=response)
    self.game.log('The runner takes 3 net damage and a tag.')
    self.game.insert_next_phase(
        timing_phases.TakeTags(self.game, self.game.runner, 1))
    self.game.runner.tags += 1
    damage_phase = timing_phases.TakeNetDamage(self.game, self.game.runner, 3)
    self.game.insert_next_phase(damage_phase)


class NoCard01070(actions.Action):
  DESCRIPTION = 'Do not activate Card01070!'


class DecideCard01070(timing_phases.ActivateAbilityChoice):
  """Choose whether to activate Card01070!"""

  def __init__(self, game, player):
    timing_phases.ActivateAbilityChoice.__init__(
        self, game, player,
        YesCard01070(game, player),
        NoCard01070(game, player),
        None)


class Card01070(asset.Asset):

  NAME = u'Card01070!'
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
    self.log('The runner accessed Card01070!')
    if self.location.parent == self.game.corp.rnd:
      self.game.expose_card(self)
    phase = DecideCard01070(self.game, self.player)
    self.game.insert_next_phase(phase)
    phase.begin()
    asset.Asset.on_access(self)
