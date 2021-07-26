

import sc2
from sc2.position import Point2, Point3
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units


import Enums

import States

# actions: ling runby, baneling drop, fake baneling drop, infestor drop, overlord scout, overseer scout, ovilator, baneling landmine, base denial baneling landmine

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
		self.unit_tags = units
		self.attack_location = atk_location
		self.rally_point = rally_point
		self.current_action = Enums.LingRunByState.CONSOLIDATING

		self.cooldown = 30

	@staticmethod
	def check_prereqs(bot):
		# ling speed
		# not attacking
		# enemy has 3+ bases or enemy is attacking and threat level < 1
		# have 8+ lings unassigned
		if (bot.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) == 1 and
			bot.army_state_machine.get_state() == States.ArmyStateConsolidating and
			(bot.get_num_enemy_bases() > 3 or (bot.get_num_enemy_bases() > 2 and bot.enemy_army_state == Enums.EnemyArmyState.MOVING_TO_ATTACK and bot.threat_level < 1)) and
			len(bot.units(UnitTypeId.ZERGLING).tags_in(bot.main_army_left + bot.main_army_right)) > 8):
			return True
		return False

	def check_cancel_conditions(self):
		# all lings are dead
		if len(self.unit_tags) == 0 or len(self.bot.units.tags_in(self.unit_tags)) == 0:
			return True
		# we launch an attack
		if self.bot.army_state_machine.get_state() == States.ArmyStateRallying or self.bot.army_state_machine.get_state() == States.ArmyStateAttacking:
			return True
		# all workers are dead at attack location
		# attack location is well defended
		# enemy army is near attack location
		if self.bot.enemy_main_army_position.distance_to(self.attack_location) < 20:
			return True	
		return False

	async def run_action(self):
		# check cancel conditions

		if self.current_action == Enums.LingRunByState.CONSOLIDATING:
			ready = True
			center = self.bot.units.tags_in(self.unit_tags).center
			for ling in self.bot.units.tags_in(self.unit_tags):
				if ling.distance_to_squared(center) > 25:
					self.bot.client.debug_sphere_out(ling.position3d, 1, color = Point3((255, 0, 255)))
					self.bot.do(ling.move(center))
					ready = False
				else:
					self.bot.client.debug_sphere_out(ling.position3d, 1, color = Point3((0, 255, 255)))
			if ready:
				self.current_action = Enums.LingRunByState.MOVING_TO_RALLY
		elif self.current_action == Enums.LingRunByState.MOVING_TO_RALLY:
			ready = True
			for ling in self.bot.units.tags_in(self.unit_tags):
				if ling.distance_to_squared(self.rally_point) > 25:
					self.bot.do(ling.move(self.rally_point))
					ready = False
			if ready:
				self.current_action = Enums.LingRunByState.ATTACKING
		elif self.current_action == Enums.LingRunByState.ATTACKING:
			for ling in self.bot.units.tags_in(self.unit_tags):
				if ling.distance_to_squared(self.attack_location) > 100 or ling.is_idle:
					self.bot.do(ling.attack(self.attack_location))


class BaseDenialLandmine(SpecialAction):
	def __init__(self, bot, units, attack_location, rally_point):
		super().__init__(bot)
		self.unit_tags = list(units)
		self.rally_point = rally_point
		self.bane_positions = [attack_location.towards(rally_point, 4.2), attack_location.towards(bot.start_location, 4.2)]
		self.current_action = Enums.BanelingLandmineState.RALLYING

	@staticmethod
	def check_prereqs(bot):
		# burrow researched
		# not attacking
		# at least 2 banelings
		if (bot.already_pending_upgrade(UpgradeId.BURROW) == 1 and
			bot.army_state_machine.get_state() == 'Consolidating' and
			len(bot.units(UnitTypeId.BANELING).tags_in(bot.main_army_left + bot.main_army_right)) >= 2):
			print("can send landmine")
			return True
		return False

	def check_cancel_conditions(self):
		# enemy buildings at attack location
		# enemy units at attack location
		# either bane is dead
		if len(self.unit_tags) < 2 or len(self.bot.units.tags_in(self.unit_tags)) < 2:
			return True

	async def run_action(self):
		if self.current_action == Enums.BanelingLandmineState.RALLYING:
			in_position = True
			for bane in self.bot.units.tags_in(self.unit_tags):
				if bane.position.distance_to(self.rally_point) > 5:
					in_position = False
					self.bot.do(bane.move(self.rally_point))
			if in_position:
				self.current_action = Enums.BanelingLandmineState.MOVING_TO_POSITION
		elif self.current_action == Enums.BanelingLandmineState.MOVING_TO_POSITION:
			for i in range(0, len(self.unit_tags)):
				if not self.bot.tag_to_unit.get(self.unit_tags[i]).is_burrowed and self.bot.tag_to_unit.get(self.unit_tags[i]).position.distance_to(self.bane_positions[i]) < .2:
					self.bot.do(self.bot.tag_to_unit.get(self.unit_tags[i])(AbilityId.BURROWDOWN_BANELING))
				else:
					self.bot.do(self.bot.tag_to_unit.get(self.unit_tags[i]).move(self.bane_positions[i]))
			for bane in self.bot.units.tags_in(self.unit_tags):
				if not bane.is_burrowed:
					return
			self.current_action = Enums.BanelingLandmineState.WAITING_TO_DETONATE
		elif self.current_action == Enums.BanelingLandmineState.WAITING_TO_DETONATE:
			if len(self.bot.enemy_structures({UnitTypeId.HATCHERY, UnitTypeId.COMMANDCENTER, UnitTypeId.NEXUS})) > 0 and self.bane_positions[0].distance_to_closest(self.bot.enemy_structures({UnitTypeId.HATCHERY, UnitTypeId.COMMANDCENTER, UnitTypeId.NEXUS})) < 5:
				for bane in self.bot.units.tags_in(self.unit_tags):
					self.bot.do(bane(AbilityId.EXPLODE_EXPLODE))






class Ovilator(SpecialAction):
	def __init__(self, bot, ovis, units, low_ground_pos, high_ground_pos):
		super().__init__(bot)
		self.dropperlords = ovis
		self.unit_tags = units
		self.low_ground_rally = low_ground_pos
		self.ovi_position = high_ground_pos
		self.current_action = Enums.OvilatorState.CONSOLIDATING


	@staticmethod
	def check_prereqs(bot):
		# ovi speed
		# enemy doesnt have triange 3rd
		if (bot.already_pending_upgrade(UpgradeId.OVERLORDSPEED) < 1 or
			True):
			return False
		return True

	def check_cancel_conditions(self):
		# all dropperlords are dead
		if len(self.dropperlords) == 0 or len(self.bot.units.tags_in(self.dropperlords)) == 0:
			return True
		# high ground position is blocked or well defended
		return False

	async def run_action(self):

		if self.current_action == Enums.OvilatorState.CONSOLIDATING:
			pass
		elif self.current_action == Enums.OvilatorState.MOVING_TO_POSITION:
			pass
		elif self.current_action == Enums.OvilatorState.ELEVATORING:
			pass