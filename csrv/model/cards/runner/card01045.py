from csrv.model.cards import card_info
from csrv.model.cards import program


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

  def build_actions(self):
    program.Program.build_actions(self)
