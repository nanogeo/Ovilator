

import sc2
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units


import Enums


class SpecialAction:
	def __init__(self, bot):
		self.bot = bot

	@staticmethod
	def check_prereqs():
		print("Error check_prereqs called on SpecialAction base class")

	def check_cancel_conditions(self):
		print("Error check_cancel_conditions called on SpecialAction base class")

	async def run_action(self):
		print("Error run_action called on SpecialAction base class")
		

class LingRunby(SpecialAction):
	def __init__(self, bot, units, atk_location, rally_point):
		super().__init__(bot)
		self.attack_location = None
		self.unit_tags = units
		self.attack_location = atk_location
		self.rally_point = rally_point
		self.current_action = 'CONSILIDATING'

	@staticmethod
	def check_prereqs(bot):
		# ling speed
		# not attacking
		# enemy has 3+ bases or enemy is attacking and threat level < 1
		# have 8+ lings unassigned
		if (bot.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) < 1 or
			bot.army_state != Enums.ArmyState.CONSOLIDATING or
			not (sum(bot.enemy_expos) + 1 > 3 or (bot.enemy_army_state == Enums.EnemyArmyState.MOVING_TO_ATTACK and bot.threat_level < 1)) or
			bot.units(UnitTypeId.ZERGLING).tags_in(bot.main_army_left + bot.main_army_right) < 8):
			return False
		return True

	def check_cancel_conditions(self):
		# all lings are dead
		# all workers are dead at attack location
		# attack location is well defended
		
		pass

	async def run_action(self):
		# check cancel conditions

		if self.current_action == 'CONSOLIDATING':
			ready = True
			center = self.bot.units.tags_in(self.unit_tags).center
			for ling in self.bot.units.tags_in(self.unit_tags):
				if ling.distance_to_squared(center) > 25:
					self.bot.do(ling.move(center))
					ready = False
			if ready:
				self.current_action = 'MOVING_TO_RALLY'
		elif self.current_action == 'MOVING_TO_RALLY':
			ready = True
			for ling in self.bot.units.tags_in(self.unit_tags):
				if ling.distance_to_squared(self.rally_point) > 25:
					self.bot.do(ling.move(self.rally_point))
					ready = False
			if ready:
				self.current_action = 'ATTACKING'
		elif self.current_action == 'ATTACKING':
			for ling in self.bot.units.tags_in(self.unit_tags):
				if ling.distance_to_squared(self.attack_location) > 100 or ling.is_idle:
					self.bot.do(ling.attack(self.attack_location))


all_actions = [LingRunby]