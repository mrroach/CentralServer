from csrv.model import actions
from csrv.model import events
from csrv.model.cards import card_info
from csrv.model.cards import program
from csrv.model import timing_phases


class Card01028RunAction(actions.MakeARunAction):

  def __init__(self, game, player, card01028):
    actions.MakeARunAction.__init__(self, game, player, game.corp.archives)
    self.card01028 = card01028

  def resolve(self, params=None):
    self.card01028.setup_card01028()
    actions.MakeARunAction.resolve(
        self, params, ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)

  @property
  def description(self):
    return ('[click]: Make a run on archives, if successful, treat as '
            'a successful run on R&D')


class Card01028(program.Program):

  NAME = u'Card01028'
  SET = card_info.CORE
  NUMBER = 28
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 3
  UNIQUE = False
  COST = 4
  MEMORY = 2
  IMAGE_SRC = '01028.png'

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnActions: 'card01028_actions',
  }

  def build_actions(self):
    program.Program.build_actions(self)

  def card01028_actions(self):
    return [Card01028RunAction(self.game, self.player, self)]

  def setup_card01028(self):
    self.game.register_listener(events.ApproachServer_4_4, self)

  def on_approach_server_4_4(self, event, sender):
    # The old switcheroo
    # TODO(mrroach): Make this into a conditional static trigger
    if self.game.run.server == self.game.corp.archives:
      self.game.run.server = self.game.corp.hq
    self.game.deregister_listener(events.ApproachServer_4_4, self)

