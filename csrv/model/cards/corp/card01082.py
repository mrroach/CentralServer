from csrv.model import events
from csrv.model import timing_phases

from csrv.model.cards import agenda
from csrv.model.cards import card_info


class Card01082(agenda.Agenda):

  NAME = u'Card01082'
  SET = card_info.CORE
  NUMBER = 82
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  UNIQUE = False
  ADVANCEMENT_REQUIREMENT = 2
  AGENDA_POINTS = 1
  IMAGE_SRC = '01082.png'

  def build_actions(self):
    agenda.Agenda.build_actions(self)

  def score(self):
    agenda.Agenda.score(self)
    self.log('The runner takes 2 tags from Card01082')
    self.game.insert_next_phase(
        timing_phases.TakeTags(self.game, self.game.runner, 2))
    self.game.register_listener(events.CorpTurnEnd, self)

  def on_corp_turn_end(self, sender, event):
    self.game.deregister_listener(events.CorpTurnEnd, self)
    self.log('The runner loses 2 tags from Card01082')
    self.game.runner.tags = max(self.game.runner.tags - 2, 0)
