from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import resource


class PreventATag(actions.Action):
  DESCRIPTION = 'Prevent a tag'

  def is_usable(self):
    return (actions.Action.is_usable(self) and
            bool(self.game.current_phase().tags))

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.Action.resolve(
        self, response=response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.game.current_phase().tags -= 1
    self.card.trash()


class Card01032(resource.Resource):

  NAME = u'Card01032'
  SET = card_info.CORE
  NUMBER = 32
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.CONNECTION,
  ])
  COST = 1
  IMAGE_SRC = '01032.png'

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.TakeTags: 'prevent_tag_actions',
  }

  def build_actions(self):
    resource.Resource.build_actions(self)
    self._prevent_a_tag = PreventATag(self.game, self.player, self)

  def prevent_tag_actions(self):
    return [self._prevent_a_tag]
