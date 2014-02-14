from csrv.model import actions
from csrv.model import cost
from csrv.model import events
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import program


class PreventNetDamage(actions.Action):
  DESCRIPTION = 'Prevent the first net damage this turn'

  def __init__(self, game, player, card):
    cost_obj = cost.Cost(game, player, clicks=0, credits=1)
    actions.Action.__init__(self, game, player, card, cost=cost_obj)

  def is_usable(self):
    current_turn = self.game.corp_turn_count + self.game.runner_turn_count
    phase = self.game.current_phase()
    return (actions.Action.is_usable(self) and not
            self.card.last_net_damage_turn == current_turn and
            phase.damage == phase.original_damage and
            phase.damage)

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.Action.resolve(
        self, response=response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.game.current_phase().damage -= 1


class Card01045(program.Program):

  NAME = u'Card01045'
  SET = card_info.CORE
  NUMBER = 45
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 1
  UNIQUE = False
  COST = 2
  MEMORY = 1
  IMAGE_SRC = '01045.png'

  LISTENS = [
      events.EndTakeNetDamage,
  ]

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.TakeNetDamage: 'prevent_net_damage_actions',
  }

  def __init__(self, game, player):
    program.Program.__init__(self, game, player)
    self.last_net_damage_turn = -1

  def build_actions(self):
    program.Program.build_actions(self)
    self._prevent_net_damage = PreventNetDamage(self.game, self.player, self)

  def on_end_take_net_damage(self, sender, event):
    self.last_net_damage_turn = (
        self.game.corp_turn_count + self.game.runner_turn_count)

  def prevent_net_damage_actions(self):
    return [self._prevent_net_damage]
