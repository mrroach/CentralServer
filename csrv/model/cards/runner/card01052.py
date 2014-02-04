from csrv.model.cards import card_info
from csrv.model.cards import resource


class Card01052(resource.Resource):

  NAME = u'Card01052'
  SET = card_info.CORE
  NUMBER = 52
  SIDE = card_info.RUNNER
  FACTION = card_info.NEUTRAL
  INFLUENCE = 0
  UNIQUE = False
  KEYWORDS = set([
      card_info.LINK,
  ])
  COST = 1
  IMAGE_SRC = '01052.png'

  def build_actions(self):
    resource.Resource.build_actions(self)

  def on_install(self):
    resource.Resource.on_install(self)
    self.player.link.gain(1)

  def on_uninstall(self):
    resource.Resource.on_uninstall(self)
    self.player.link.lose(1)
