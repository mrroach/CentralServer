import unittest
from csrv.model import modifiers
from csrv.model import test_base
from csrv.model.cards import ice


class IceTest(test_base.TestBase):
  def setUp(self):
    test_base.TestBase.setUp(self)
    self.card = ice.Ice(self.game, self.corp)
    server = self.game.corp.new_remote_server()
    server.install(self.card)
    self.card.COST = 4
    self.card.STRENGTH = 4

  def test_cost_works_without_modifiers(self):
    self.assertEqual(4, self.card.cost)

  def test_cost_honors_card_modifiers(self):
    mod = modifiers.IceRezCostModifier(self.game, -1, card=self.card)
    self.assertEqual(3, self.card.cost)
    mod.remove()
    self.assertEqual(4, self.card.cost)

  def test_cost_honors_global_modifiers(self):
    mod = modifiers.IceRezCostModifier(self.game, -1)
    self.assertEqual(3, self.card.cost)
    mod.remove()
    self.assertEqual(4, self.card.cost)

  def test_strength_works_without_modifiers(self):
    self.assertEqual(4, self.card.strength)

  def test_strength_honors_card_modifiers(self):
    mod = modifiers.IceStrengthModifier(self.game, -1, card=self.card)
    self.assertEqual(3, self.card.strength)
    mod.remove()
    self.assertEqual(4, self.card.strength)

  def test_strength_honors_global_modifiers(self):
    mod = modifiers.IceStrengthModifier(self.game, -1)
    self.assertEqual(3, self.card.strength)
    mod.remove()
    self.assertEqual(4, self.card.strength)


if __name__ == '__main__':
  unittest.main()
