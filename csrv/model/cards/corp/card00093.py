from csrv.model import events
from csrv.model.cards import card_info
from csrv.model.cards import corp_identity


class Card00093(corp_identity.CorpIdentity):

  NAME = u'Card00093'
  SET = card_info.CORE
  NUMBER = 93
  SIDE = card_info.CORP
  FACTION = card_info.MEATCORP
  UNIQUE = False
  KEYWORDS = set([
      card_info.MEGACORP,
  ])
  IMAGE_SRC = '01093.png'

  LISTENS = [
      events.PlayOperation
  ]

  def build_actions(self):
    identity.Identity.build_actions(self)

  def on_play_operation(self, sender, event):
    if card_info.TRANSACTION in sender.KEYWORDS:
      self.log('The corp gains 1[cred] for playing a transaction')
      self.player.credits.gain(1)

