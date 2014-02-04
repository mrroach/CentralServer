import unittest
from csrv.model import modifiers
from csrv.model import test_base
from csrv.model.cards import program


class ProgramTest(test_base.TestBase):
  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = program.Program(self.game, self.runner)
    self.card.COST = 4
    self.card.STRENGTH = 4

  def test_cost_works_without_modifiers(self):
    self.assertEqual(4, self.card.cost)

  def test_cost_honors_card_modifiers(self):
    mod = modifiers.ProgramCostModifier(self.game, -1, card=self.card)
    self.assertEqual(3, self.card.cost)
    mod.remove()
    self.assertEqual(4, self.card.cost)

  def test_cost_honors_global_modifiers(self):
    mod = modifiers.ProgramCostModifier(self.game, -1)
    self.assertEqual(3, self.card.cost)
    mod.remove()
    self.assertEqual(4, self.card.cost)

  def test_strength_works_without_modifiers(self):
    self.assertEqual(4, self.card.strength)

  def test_strength_honors_card_modifiers(self):
    mod = modifiers.ProgramStrengthModifier(self.game, -1, card=self.card)
    self.assertEqual(3, self.card.strength)
    mod.remove()
    self.assertEqual(4, self.card.strength)

  def test_strength_honors_global_modifiers(self):
    mod = modifiers.ProgramStrengthModifier(self.game, -1)
    self.assertEqual(3, self.card.strength)
    mod.remove()
    self.assertEqual(4, self.card.strength)


if __name__ == '__main__':
  unittest.main()
