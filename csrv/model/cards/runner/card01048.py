from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import resource


class PreventTrash(actions.Action):
  DESCRIPTION = 'Prevent trashing a program or piece of hardware'

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.Action.resolve(
        self, response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.card.trash()
    self.game.current_phase().end_phase()


class Card01048(resource.Resource):

  NAME = u'Card01048'
  SET = card_info.CORE
  NUMBER = 48
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.REMOTE,
  ])
  COST = 0
  IMAGE_SRC = '01048.png'

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.TrashAProgram: 'prevent_trash_actions'
  }

  def build_actions(self):
    resource.Resource.build_actions(self)
    self._prevent_trash = PreventTrash(self.game, self.player, card=self)

  def prevent_trash_actions(self):
    return [self._prevent_trash]
