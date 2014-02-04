from csrv.model.cards import card_info
from csrv.model import modifiers
from csrv.model.cards import resource
from csrv.model import events


class Card01015(resource.Resource):

  NAME = u'Card01015'
  SET = card_info.CORE
  NUMBER = 15
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 3
  UNIQUE = True
  KEYWORDS = set([
      card_info.VIRTUAL,
  ])
  COST = 3
  IMAGE_SRC = '01015.png'

  WHEN_INSTALLED_LISTENS = [
      events.BeginEncounterIce_3_1,
  ]

  def on_begin_encounter_ice_3_1(self, sender, event):
    modifiers.IceStrengthModifier(
        self.game, -1,
        card=self.game.run.current_ice(),
        until=events.EndEncounterIce_3_2)

  def build_actions(self):
    resource.Resource.build_actions(self)
