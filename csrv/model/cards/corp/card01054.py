from csrv.model.cards import card_info
from csrv.model.cards import corp_identity
from csrv.model import events
from csrv.model import actions
from csrv.model import pool


class Card01054(corp_identity.CorpIdentity):

  NAME = 'Card01054'
  SUBTYPES = [card_info.MEGACORP]
  FACTION = card_info.ROBOCORP
  NUMBER = 54
  IMAGE_SRC = '01054.png'
  SET = card_info.CORE

  LISTENS = [
      events.InstallAgendaAssetUpgrade,
      events.InstallIce,
  ]

  def __init__(self, *args, **kwargs):
    corp_identity.CorpIdentity.__init__(self, *args, **kwargs)
    self.ability_used_on_turn = None

  def on_install_agenda_asset_upgrade(self, sender, event):
    turn = self.game.corp_turn_count + self.game.runner_turn_count
    if not self.ability_used_on_turn == turn:
      self.log('The corp gains 1[cred] for installing')
      self.ability_used_on_turn = turn
      self.player.credits.gain(1)

  on_install_ice = on_install_agenda_asset_upgrade


