# -*- coding: utf-8 -*-
"""
Created on Thu May 27 17:12:28 2021

@author: hocke
"""

import sc2
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units

import time
import math

import Enums


class Plan:
	@staticmethod
	def test_conditions(bot):
		return 0
	
	@staticmethod
	async def execute_plan(bot):
		print("Error execute_plan called on Plan class")
		
	
	@staticmethod    
	async def make_overlords(bot):
		# Make Overlords
		all_larva = bot.units(UnitTypeId.LARVA)
		if len(all_larva) == 0:
			return True
		current_cap = bot.supply_cap
		i = 0
		while (i < len(all_larva) and bot.supply_cap < 200 and
			   ((bot.supply_used / current_cap >= .8 and not bot.already_pending(UnitTypeId.OVERLORD) > 0) or 
				(bot.supply_used / current_cap >= .9 and not bot.already_pending(UnitTypeId.OVERLORD) > 1))):
			if bot.minerals >= 100:
				bot.do(all_larva[i].train(UnitTypeId.OVERLORD))
				f = open("overlord_times.txt", "a")
				f.write("Larva #" + str(i) + " Overlord #" + str(len(bot.units(UnitTypeId.OVERLORD)) + 1) + " Supply used: " + str(bot.supply_used) + " Supply cap: " + str(bot.supply_cap) + " Time: " + bot.time_formatted + "\n")
				f.close()
				i += 1
				current_cap += 8
			else:
				return False

		# make overseers
		if not bot.make_overseers():
			bot.add_debug_info("failed to make overseers")
			return False
		return True
	
	@staticmethod
	async def make_army(bot):
		print("Error make_army called on Plan class")
	
	@staticmethod
	async def make_drones(bot):
		print("Error make_drones called on Plan class")
	
	@staticmethod
	async def make_expansions(bot):
		print("Error make_expansions called on Plan class")
	
	@staticmethod
	async def expand_tech(bot):
		print("Error expand_tech called on Plan class")
	
	@staticmethod
	async def get_upgrades(bot):
		print("Error get_upgrades called on Plan class")

	@staticmethod
	async def micro(bot):
		print("Error micro called on Plan class")
	

class LingBaneHydraBase(Plan):
	@staticmethod
	def test_conditions(bot):
		value = super(LingBaneHydraBase, LingBaneHydraBase).test_conditions(bot)
		if bot.get_army_comp() == Enums.ArmyComp.LING_BANE_HYDRA:
			value += 5
		else:
			value -= 100
		
		return value

	@staticmethod
	async def execute_plan(bot):
		print("Error execute_plan called on LingBaneHydraBase class")

	@staticmethod
	async def make_drones(bot):
		# Queens
		queen_need = min(8, len(bot.townhalls.ready) * 2 + 2)
		if len(bot.units(UnitTypeId.QUEEN)) + bot.already_pending(UnitTypeId.QUEEN) < queen_need and bot.supply_used + 2 <= bot.supply_cap and len(bot.townhalls.ready.idle) > 0:
			if bot.minerals >= 150:
				await bot.build_queen()
				f = open("queen_times.txt", "a")
				f.write("Current Queens: " + str(len(bot.units(UnitTypeId.QUEEN)) + bot.already_pending(UnitTypeId.QUEEN)) + " Queen need: " + str(queen_need) + " Time: " + bot.time_formatted + "\n")
				f.close()
			else:
				return False
			
		# Larva
		all_larva = bot.units(UnitTypeId.LARVA)
		if len(all_larva) == 0:
			return True
		i = 0
		drone_need = min(80, len(bot.townhalls) * 16 + len(bot.structures(UnitTypeId.EXTRACTOR)) * 3)
		while (i < len(all_larva) and bot.supply_workers + bot.already_pending(UnitTypeId.DRONE) < drone_need and bot.supply_used + 1 + i <= bot.supply_cap):
			if bot.minerals >= 50:
				bot.do(all_larva[i].train(UnitTypeId.DRONE))
				g = open("drone_times.txt", "a")
				g.write("Larva #" + str(i) + " Current Drones: " + str(bot.supply_workers + bot.already_pending(UnitTypeId.DRONE)) + " Drone need: " + str(drone_need) + " Time: " + bot.time_formatted + "\n")
				g.close()            
				drone_need -= 1
				i += 1
			else:
				return False
		return True
		
	@staticmethod
	async def make_expansions(bot):
		if (sum(bot.enemy_expos) + 1 >= len(bot.townhalls) + bot.already_pending(UnitTypeId.HATCHERY)) or (bot.minerals > 600 and not bot.already_pending(UnitTypeId.HATCHERY)):
			if bot.minerals >= 300:
				bot.add_debug_info("make exop")
				bot.last_expansion_time = bot.time
				expansion_location = await bot.get_next_expansion()
				builder_drone = bot.select_build_worker(expansion_location)
				bot.remove_drone(builder_drone.tag)
				bot.do(builder_drone.build(UnitTypeId.HATCHERY, expansion_location))
			else:
				bot.add_debug_info("not enough to make expo")
				return False
		return True
	
	@staticmethod
	async def expand_tech(bot):
		# 4:00 - evo
		# finished evo - +1 melee
		# 5:00 - lair
		# 5:10 - bane nest
		# lair and bane nest - bane speed
		# lair - hydra den
		# hydra den - both hydra upgrades
		# +1 melee - +2 melee
		
		if bot.time > 240:
			if bot.vespene < 500 and (bot.time > 360 or len(bot.structures(UnitTypeId.EXTRACTOR)) < 2):
				if bot.minerals >= 25:
					await bot.build_extractor()
				else:
					return False
		
		if bot.time > 240:
			if len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER)) < 1:
				if bot.can_afford(UnitTypeId.EVOLUTIONCHAMBER):
					await bot.build_building(UnitTypeId.EVOLUTIONCHAMBER)
				else:
					return False
		
		if bot.time > 300:
			if len(bot.structures(UnitTypeId.LAIR)) + len(bot.structures(UnitTypeId.HIVE)) == 0 and not bot.already_pending(UnitTypeId.LAIR):
				if bot.can_afford(AbilityId.UPGRADETOLAIR_LAIR):
					try: 
						hatch = bot.townhalls.ready.idle.random
					except:
						print("no hatches")
					else:
						for ability in await bot.get_available_abilities(hatch):
							if ability == AbilityId.UPGRADETOLAIR_LAIR:
								bot.do(hatch(AbilityId.UPGRADETOLAIR_LAIR))
				else:
					return False
		
		if bot.time > 310:
			if len(bot.structures(UnitTypeId.BANELINGNEST)) == 0:
				if bot.can_afford(UnitTypeId.BANELINGNEST):
					await bot.build_building(UnitTypeId.BANELINGNEST)
				else:
					return False
		
		if len(bot.structures(UnitTypeId.LAIR)) + len(bot.structures(UnitTypeId.HIVE)) > 0 and len(bot.structures(UnitTypeId.HYDRALISKDEN)) + bot.already_pending(UnitTypeId.HYDRALISKDEN) == 0:
			if bot.can_afford(UnitTypeId.HYDRALISKDEN):
				await bot.build_building(UnitTypeId.HYDRALISKDEN)
			else:
				return False
		

		
		return True
			
	@staticmethod
	async def make_army(bot):
		if len(bot.structures(UnitTypeId.SPAWNINGPOOL).ready) == 0:
			return False
		all_larva = bot.units(UnitTypeId.LARVA)
		if len(all_larva) == 0:
			return True
		i = 0
		zerglings = (len(bot.units(UnitTypeId.ZERGLING)) + bot.already_pending(UnitTypeId.ZERGLING)) / bot.unit_ratio[0]
		banelings = (len(bot.units({UnitTypeId.BANELING, UnitTypeId.BANELINGCOCOON}))) / bot.unit_ratio[1]
		hydralisks = (len(bot.units(UnitTypeId.HYDRALISK)) + bot.already_pending(UnitTypeId.HYDRALISK)) / bot.unit_ratio[2]
		
		
		while (i < len(all_larva) and bot.supply_used + 1 + i <= bot.supply_cap):
			if len(bot.structures(UnitTypeId.HYDRALISKDEN)) > 0:
				if len(bot.structures(UnitTypeId.BANELINGNEST)) > 0 and len(bot.units(UnitTypeId.ZERGLING).ready) > 0:
					if zerglings <= hydralisks and zerglings <= banelings:
						# make lings
						if bot.can_afford(UnitTypeId.ZERGLING):
							bot.do(all_larva[i].train(UnitTypeId.ZERGLING))
							i += 1
							zerglings += 2 / bot.unit_ratio[0]
						else:
							return False
					elif banelings <= zerglings and banelings <= hydralisks:
						# make banes
						if bot.can_afford(UnitTypeId.BANELING):
							bot.make_baneling()
							banelings += 1 / bot.unit_ratio[1]
							zerglings -= 1 / bot.unit_ratio[0]
						else:
							return False
					else:
						# make hydras
						if bot.can_afford(UnitTypeId.HYDRALISK):
							bot.do(all_larva[i].train(UnitTypeId.HYDRALISK))
							i += 1
							hydralisks += 1 / bot.unit_ratio[2]
						else:
							return False
				else:
					if zerglings <= hydralisks:
						# make lings
						if bot.can_afford(UnitTypeId.ZERGLING):
							bot.do(all_larva[i].train(UnitTypeId.ZERGLING))
							i += 1
							zerglings += 2 / bot.unit_ratio[0]
						else:
							return False
					else:
						# makes hydras
						if bot.can_afford(UnitTypeId.HYDRALISK):
							bot.do(all_larva[i].train(UnitTypeId.HYDRALISK))
							i += 1
							hydralisks += 1 / bot.unit_ratio[2]
						else:
							return False
			elif len(bot.structures(UnitTypeId.BANELINGNEST)) > 0 and len(bot.units(UnitTypeId.ZERGLING).ready) > 0:
				if zerglings <= banelings:
					# make lings
					if bot.can_afford(UnitTypeId.ZERGLING):
						bot.do(all_larva[i].train(UnitTypeId.ZERGLING))
						i += 1
						zerglings += 2 / bot.unit_ratio[0]
					else:
						return False
				else:
					# make banes
					if bot.can_afford(UnitTypeId.BANELING):
						bot.make_baneling()
						banelings += 1 / bot.unit_ratio[1]
						zerglings -= 1 / bot.unit_ratio[0]
					else:
						return False
			else:
				# make lings
				if bot.can_afford(UnitTypeId.ZERGLING):
					bot.do(all_larva[i].train(UnitTypeId.ZERGLING))
					i += 1
					zerglings += 2 / bot.unit_ratio[0]
				else:
					return False
					
		return True
		
	@staticmethod
	async def get_upgrades(bot):
		# ling speed
		if bot.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) == 0 and len(bot.structures(UnitTypeId.SPAWNINGPOOL).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.SPAWNINGPOOL, UpgradeId.ZERGLINGMOVEMENTSPEED, AbilityId.RESEARCH_ZERGLINGMETABOLICBOOST)
		# ovi speed
		if bot.already_pending_upgrade(UpgradeId.OVERLORDSPEED) == 0 and len(bot.structures(UnitTypeId.HATCHERY).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.HATCHERY, UpgradeId.OVERLORDSPEED, AbilityId.RESEARCH_PNEUMATIZEDCARAPACE)
		# +1 melee, +1 carapace
		if bot.already_pending_upgrade(UpgradeId.ZERGMELEEWEAPONSLEVEL1) == 0 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.EVOLUTIONCHAMBER, UpgradeId.ZERGMELEEWEAPONSLEVEL1, AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL1)
		if bot.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL1) == 0 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.EVOLUTIONCHAMBER, UpgradeId.ZERGGROUNDARMORSLEVEL1, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1)
		# lair
		if len(bot.structures({UnitTypeId.LAIR, UnitTypeId.HIVE}).ready) == 0:
			return True
		# baneling speed
		if bot.already_pending_upgrade(UpgradeId.CENTRIFICALHOOKS) == 0 and len(bot.structures(UnitTypeId.BANELINGNEST).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.BANELINGNEST, UpgradeId.CENTRIFICALHOOKS, AbilityId.RESEARCH_CENTRIFUGALHOOKS)
		# burrow
		if bot.already_pending_upgrade(UpgradeId.BURROW) == 0 and len(bot.structures(UnitTypeId.HATCHERY).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.HATCHERY, UpgradeId.BURROW, AbilityId.RESEARCH_BURROW)
		# +2/+2
		if bot.already_pending_upgrade(UpgradeId.ZERGMELEEWEAPONSLEVEL2) == 0 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.EVOLUTIONCHAMBER, UpgradeId.ZERGMELEEWEAPONSLEVEL2, AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2)
		if bot.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL2) == 0 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.EVOLUTIONCHAMBER, UpgradeId.ZERGGROUNDARMORSLEVEL2, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2)
		# hydra speed
		if bot.already_pending_upgrade(UpgradeId.EVOLVEMUSCULARAUGMENTS) == 0 and len(bot.structures(UnitTypeId.HYDRALISKDEN).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.HYDRALISKDEN, UpgradeId.EVOLVEMUSCULARAUGMENTS, AbilityId.RESEARCH_MUSCULARAUGMENTS)
		# hydra range
		if bot.already_pending_upgrade(UpgradeId.EVOLVEGROOVEDSPINES) == 0 and len(bot.structures(UnitTypeId.HYDRALISKDEN).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.HYDRALISKDEN, UpgradeId.EVOLVEGROOVEDSPINES, AbilityId.RESEARCH_GROOVEDSPINES)
		# hive
		if len(bot.structures(UnitTypeId.HIVE).ready) == 0:
			return True
		# adrenal
		if bot.already_pending_upgrade(UpgradeId.ZERGLINGATTACKSPEED) == 0 and len(bot.structures(UnitTypeId.SPAWNINGPOOL).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.SPAWNINGPOOL, UpgradeId.ZERGLINGATTACKSPEED, AbilityId.RESEARCH_ZERGLINGADRENALGLANDS)
		# +3/+3
		if bot.already_pending_upgrade(UpgradeId.ZERGMELEEWEAPONSLEVEL3) == 0 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.EVOLUTIONCHAMBER, UpgradeId.ZERGMELEEWEAPONSLEVEL3, AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3)
		if bot.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL3) == 0 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.EVOLUTIONCHAMBER, UpgradeId.ZERGGROUNDARMORSLEVEL3, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3)
		
		return True
	
class MacroLingBaneHydra(LingBaneHydraBase):
	@staticmethod
	def to_string():
		return "LBH Macro"
	
	@staticmethod
	def test_conditions(bot):
		value = super(MacroLingBaneHydra, MacroLingBaneHydra).test_conditions(bot)
		if bot.threat_level <= .8:
			value += 5
		if bot.difference_in_bases < 1:
			value += 2
		if bot.saturation < 1:
			value += 2
		return value
	
	@staticmethod
	async def execute_plan(bot):
		if await MacroLingBaneHydra.make_overlords(bot):
			if await MacroLingBaneHydra.make_expansions(bot):
				if await MacroLingBaneHydra.expand_tech(bot):
					if await MacroLingBaneHydra.make_drones(bot):
						await MacroLingBaneHydra.make_army(bot)
					else:
						bot.add_debug_info("failed to make drones")
				else:
					bot.add_debug_info("failed to expand tech")
			else:
				bot.add_debug_info("failed to make expansions")
		else:
			bot.add_debug_info("failed to make overlords")

	
	@staticmethod
	async def expand_tech(bot):
		
		if bot.vespene > 100 and not await MacroLingBaneHydra.get_upgrades(bot):
			bot.add_debug_info("failed to get upgrades")
			return False
		
		if bot.time > 240 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER)) < 1:
			# build evo chamber
			if bot.can_afford(UnitTypeId.EVOLUTIONCHAMBER):
				await bot.build_building(UnitTypeId.EVOLUTIONCHAMBER)
			else:
				return False
		elif bot.time > 240 and len(bot.structures(UnitTypeId.EXTRACTOR)) < 2:
			# build 2nd gas
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_extractor()
			else:
				return False
		elif bot.time > 300 and len(bot.structures({UnitTypeId.LAIR, UnitTypeId.HIVE})) + bot.already_pending(UnitTypeId.LAIR) == 0:
			# build lair
			if bot.can_afford(AbilityId.UPGRADETOLAIR_LAIR):
					try: 
						hatch = bot.townhalls.ready.idle.random
					except:
						print("no hatches")
					else:
						for ability in await bot.get_available_abilities(hatch):
							if ability == AbilityId.UPGRADETOLAIR_LAIR:
								bot.do(hatch(AbilityId.UPGRADETOLAIR_LAIR))
			else:
				return False
		elif bot.time > 300 and len(bot.structures(UnitTypeId.EXTRACTOR)) < 3:
			# build 3rd gas
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_extractor()
			else:
				return False
		elif bot.time > 310 and len(bot.structures(UnitTypeId.BANELINGNEST)) == 0:
			# build baneling nest
			if bot.can_afford(UnitTypeId.BANELINGNEST):
				await bot.build_building(UnitTypeId.BANELINGNEST)
			else:
				return False
		elif bot.time > 310 and len(bot.structures(UnitTypeId.EXTRACTOR)) < 4:
			# build 4th gas
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_extractor()
			else:
				return False
		elif bot.time > 330 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER)) < 2:
			# build 2nd evo chamber
			if bot.can_afford(UnitTypeId.EVOLUTIONCHAMBER):
				await bot.build_building(UnitTypeId.EVOLUTIONCHAMBER)
			else:
				return False
		elif bot.time > 350 and len(bot.structures({UnitTypeId.LAIR, UnitTypeId.HIVE})) == 0:
			return True
		elif bot.time > 350 and len(bot.structures(UnitTypeId.HYDRALISKDEN)) == 0:
			# build hydra den
			if bot.can_afford(UnitTypeId.HYDRALISKDEN):
				await bot.build_building(UnitTypeId.HYDRALISKDEN)
			else:
				return False
		elif len(bot.townhalls.ready) < 3:
			bot.add_debug_info("no 3rd base")
			return True
		elif bot.time > 350 and len(bot.structures(UnitTypeId.EXTRACTOR)) < 5:
			# build 5th extractor
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_extractor()
			else:
				return False
		elif bot.time > 480 and len(bot.structures(UnitTypeId.INFESTATIONPIT)) == 0:
			# build infestation pit
			if bot.can_afford(UnitTypeId.INFESTATIONPIT):
				bot.add_debug_info("make inf pit")
				await bot.build_building(UnitTypeId.INFESTATIONPIT)
			else:
				bot.add_debug_info("can't make infestation pit")
				return False
		elif bot.time > 480 and len(bot.structures(UnitTypeId.EXTRACTOR)) < 6:
			# build 6th extractor
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_extractor()
			else:
				return False
		elif bot.time > 520 and len(bot.structures(UnitTypeId.HIVE)) + bot.already_pending(UnitTypeId.HIVE) == 0:
			# build hive
			if bot.can_afford(AbilityId.UPGRADETOLAIR_LAIR):
					try: 
						hatch = bot.structures(UnitTypeId.LAIR).ready.idle.random
					except:
						print("no lairs")
					else:
						for ability in await bot.get_available_abilities(hatch):
							if ability == AbilityId.UPGRADETOHIVE_HIVE:
								bot.do(hatch(AbilityId.UPGRADETOHIVE_HIVE))
			else:
				return False
		
		
		return True

	
	  
	
	
class BuildArmyLingBaneHydra(LingBaneHydraBase):
	@staticmethod
	def to_string():
		return "LBH Army"

	@staticmethod
	def test_conditions(bot):
		value = super(BuildArmyLingBaneHydra, BuildArmyLingBaneHydra).test_conditions(bot)
		if bot.threat_level > 1:
			value += 10
		if bot.difference_in_bases >= 1:
			value += 2
		if bot.saturation >= .6 and bot.threat_level > .75:
			value += 3
		return value

	@staticmethod
	async def execute_plan(bot):
		if await BuildArmyLingBaneHydra.make_overlords(bot):
			if await BuildArmyLingBaneHydra.make_army(bot):
				if await BuildArmyLingBaneHydra.make_drones(bot):
					if await BuildArmyLingBaneHydra.expand_tech(bot):
						await BuildArmyLingBaneHydra.make_expansions(bot)
					else:
						bot.add_debug_info("failed to expand tech")
				else:
					bot.add_debug_info("failed to make drones")
			else:
				bot.add_debug_info("failed to make army")
		else:
			bot.add_debug_info("failed to make overlords")

	
		
		
class TechLingBaneHydra(LingBaneHydraBase):
	@staticmethod
	def to_string():
		return "LBH Tech"

	@staticmethod
	def test_conditions(bot):
		value = super(TechLingBaneHydra, TechLingBaneHydra).test_conditions(bot)
		if bot.threat_level <= .75:
			value += 5
		if bot.difference_in_bases > 1:
			value += 3
		if bot.saturation >= 1:
			value += 3
		if bot.vespene < 100:
			value -= 10
		

		return value
	
	@staticmethod
	async def execute_plan(bot):
		if await TechLingBaneHydra.expand_tech(bot):
			if await TechLingBaneHydra.make_overlords(bot):
				if await TechLingBaneHydra.make_drones(bot):
					if await TechLingBaneHydra.make_army(bot):
						await TechLingBaneHydra.make_expansions(bot)
					else:
						bot.add_debug_info("failed to make army")
				else:
					bot.add_debug_info("failed to make drones")
			else:
				bot.add_debug_info("failed to make overlords")
		else:
			bot.add_debug_info("failed to make overlords")

	
	@staticmethod
	async def expand_tech(bot):
		
		if not await TechLingBaneHydra.get_upgrades(bot):
			return False
		
		if len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER)) < 1:
			# build evo chamber
			if bot.can_afford(UnitTypeId.EVOLUTIONCHAMBER):
				bot.add_debug_info("make evo 1")
				await bot.build_building(UnitTypeId.EVOLUTIONCHAMBER)
			else:
				bot.add_debug_info("can't make evo 1")
				return False
		elif len(bot.structures(UnitTypeId.EXTRACTOR)) < 2:
			# build 2nd gas
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				bot.add_debug_info("make extractor 2")
				await bot.build_extractor()
			else:
				bot.add_debug_info("can't make extractor 2")
				return False
		elif len(bot.structures({UnitTypeId.LAIR, UnitTypeId.HIVE})) + bot.already_pending(UnitTypeId.LAIR) < 1:
			bot.add_debug_info("try to make lair")
			# build lair
			if bot.can_afford(AbilityId.UPGRADETOLAIR_LAIR):
				try: 
					hatch = bot.townhalls.ready.idle.random
				except:
					bot.add_debug_info("no hatches")
				else:
					for ability in await bot.get_available_abilities(hatch):
						if ability == AbilityId.UPGRADETOLAIR_LAIR:
							bot.add_debug_info("make lair")
							bot.do(hatch(AbilityId.UPGRADETOLAIR_LAIR))
			else:
				bot.add_debug_info("can't make lair")
				return False
		elif len(bot.structures(UnitTypeId.EXTRACTOR)) < 3:
			# build 3rd gas
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				bot.add_debug_info("make extractor 3")
				await bot.build_extractor()
			else:
				bot.add_debug_info("can't make extractor 3")
				return False
		elif len(bot.structures(UnitTypeId.BANELINGNEST)) == 0:
			# build baneling nest
			if bot.can_afford(UnitTypeId.BANELINGNEST):
				bot.add_debug_info("make banenest")
				await bot.build_building(UnitTypeId.BANELINGNEST)
			else:
				bot.add_debug_info("can't make baneling nest")
				return False
		elif len(bot.structures(UnitTypeId.EXTRACTOR)) < 4:
			# build 4th gas
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_extractor()
			else:
				bot.add_debug_info("can't make extractor 4")
				return False
		elif len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER)) < 2:
			# build 2nd evo chamber
			if bot.can_afford(UnitTypeId.EVOLUTIONCHAMBER):
				bot.add_debug_info("make evo 2")
				await bot.build_building(UnitTypeId.EVOLUTIONCHAMBER)
			else:
				bot.add_debug_info("can't make evo 2")
				return False
		elif len(bot.structures({UnitTypeId.LAIR, UnitTypeId.HIVE})) == 0:
			bot.add_debug_info("no lair")
			return True
		elif len(bot.structures(UnitTypeId.HYDRALISKDEN)) == 0:
			# build hydra den
			if bot.can_afford(UnitTypeId.HYDRALISKDEN):
				bot.add_debug_info("make hydraden")
				await bot.build_building(UnitTypeId.HYDRALISKDEN)
			else:
				bot.add_debug_info("can't make hydra den")
				return False
		elif len(bot.townhalls.ready) < 3:
			bot.add_debug_info("no 3rd base")
			return True
		elif len(bot.structures(UnitTypeId.EXTRACTOR)) < 5:
			# build 5th extractor
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				bot.add_debug_info("make extractor 5")
				await bot.build_extractor()
			else:
				bot.add_debug_info("can't make extractor 5")
				return False
		elif len(bot.structures(UnitTypeId.INFESTATIONPIT)) == 0:
			# build infestation pit
			if bot.can_afford(UnitTypeId.INFESTATIONPIT):
				bot.add_debug_info("make inf pit")
				await bot.build_building(UnitTypeId.INFESTATIONPIT)
			else:
				bot.add_debug_info("can't make infestation pit")
				return False
		elif len(bot.structures(UnitTypeId.EXTRACTOR)) < 6:
			# build 6th extractor
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_extractor()
			else:
				bot.add_debug_info("can't make extractor 6")
				return False
		elif len(bot.structures(UnitTypeId.HIVE)) + bot.already_pending(UnitTypeId.HIVE) == 0:
			# build hive
			if bot.can_afford(AbilityId.UPGRADETOLAIR_LAIR):
					try: 
						hatch = bot.structures(UnitTypeId.LAIR).ready.idle.random
					except:
						bot.add_debug_info("no lairs")
					else:
						for ability in await bot.get_available_abilities(hatch):
							if ability == AbilityId.UPGRADETOHIVE_HIVE:
								bot.add_debug_info("make hive")
								bot.do(hatch(AbilityId.UPGRADETOHIVE_HIVE))
			else:
				bot.add_debug_info("can't make hive")
				return False
		
		
		return True
	
		
		
class RoachHydraBase(Plan):
	@staticmethod
	def test_conditions(bot):
		value = super(RoachHydraBase, RoachHydraBase).test_conditions(bot)
		if bot.get_army_comp() == Enums.ArmyComp.ROACH_HYDRA:
			value += 5
		else:
			value -= 100
		
		return value
	
	@staticmethod
	async def execute_plan(bot):
		print("Error execute_plan called on RoachHydraBase class")
	
	@staticmethod
	async def make_drones(bot):
		# Queens
		queen_need = min(8, len(bot.townhalls.ready) * 2 + 2)
		if len(bot.units(UnitTypeId.QUEEN)) + bot.already_pending(UnitTypeId.QUEEN) < queen_need and bot.supply_used + 2 <= bot.supply_cap and len(bot.townhalls.ready.idle) > 0:
			if bot.minerals >= 150:
				await bot.build_queen()
				f = open("queen_times.txt", "a")
				f.write("Current Queens: " + str(len(bot.units(UnitTypeId.QUEEN)) + bot.already_pending(UnitTypeId.QUEEN)) + " Queen need: " + str(queen_need) + " Time: " + bot.time_formatted + "\n")
				f.close()
			else:
				return False
			
		# Larva
		all_larva = bot.units(UnitTypeId.LARVA)
		if len(all_larva) == 0:
			return True
		i = 0
		drone_need = min(80, len(bot.townhalls) * 16 + len(bot.structures(UnitTypeId.EXTRACTOR)) * 3)
		while (i < len(all_larva) and bot.supply_workers + bot.already_pending(UnitTypeId.DRONE) < drone_need and bot.supply_used + 1 + i <= bot.supply_cap):
			if bot.minerals >= 50:
				bot.do(all_larva[i].train(UnitTypeId.DRONE))
				g = open("drone_times.txt", "a")
				g.write("Larva #" + str(i) + " Current Drones: " + str(bot.supply_workers + bot.already_pending(UnitTypeId.DRONE)) + " Drone need: " + str(drone_need) + " Time: " + bot.time_formatted + "\n")
				g.close()            
				drone_need -= 1
				i += 1
			else:
				return False
		return True

	@staticmethod
	async def make_expansions(bot):
		if (sum(bot.enemy_expos) + 1 >= len(bot.townhalls) + bot.already_pending(UnitTypeId.HATCHERY)) or (bot.minerals > 600 and not bot.already_pending(UnitTypeId.HATCHERY)):
			if bot.minerals >= 300:
				bot.last_expansion_time = bot.time
				expansion_location = await bot.get_next_expansion()
				builder_drone = bot.select_build_worker(expansion_location)
				bot.remove_drone(builder_drone.tag)
				bot.do(builder_drone.build(UnitTypeId.HATCHERY, expansion_location))
			else:
				return False
		return True

	@staticmethod
	async def expand_tech(bot):
		if bot.vespene > 100 and not await RoachHydraBase.get_upgrades(bot):
			return False

		# 4:30 - 2x evo
		# 5:00 - 2x gas, roach warren
		# 5:30 - lair, 3x gas
		# 6:30 - hydra den
		# 7:00 - inf pit
		# 8:00 - hive

		if bot.time > 270 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER)) < 2:
			# build evo chamber
			if bot.can_afford(UnitTypeId.EVOLUTIONCHAMBER):
				await bot.build_building(UnitTypeId.EVOLUTIONCHAMBER)
			else:
				return False
		elif bot.time > 300 and len(bot.structures(UnitTypeId.EXTRACTOR)) < 3:
			# build 2nd and 3rd gas
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_extractor()
			else:
				return False
		elif bot.time > 300 and len(bot.structures(UnitTypeId.ROACHWARREN)) == 0:
			# build roach warren
			if bot.can_afford(UnitTypeId.ROACHWARREN):
				await bot.build_building(UnitTypeId.ROACHWARREN)
			else:
				return False
		elif bot.time > 330 and len(bot.structures({UnitTypeId.LAIR, UnitTypeId.HIVE})) + bot.already_pending(UnitTypeId.LAIR) == 0:
			# build lair
			if bot.can_afford(AbilityId.UPGRADETOLAIR_LAIR):
					try: 
						hatch = bot.townhalls.ready.idle.random
					except:
						print("no hatches")
					else:
						for ability in await bot.get_available_abilities(hatch):
							if ability == AbilityId.UPGRADETOLAIR_LAIR:
								bot.do(hatch(AbilityId.UPGRADETOLAIR_LAIR))
			else:
				return False
		elif len(bot.townhalls.ready) < 3:
			bot.add_debug_info("no 3rd base")
			return True
		elif bot.time > 330 and len(bot.structures(UnitTypeId.EXTRACTOR)) < 6:
			# build 4th, 5th and 6th gas
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_extractor()
			else:
				return False
		elif bot.time > 390 and len(bot.structures({UnitTypeId.LAIR, UnitTypeId.HIVE})) == 0:
			return True
		elif bot.time > 390 and len(bot.structures(UnitTypeId.HYDRALISKDEN)) == 0:
			# build hydra den
			if bot.can_afford(UnitTypeId.HYDRALISKDEN):
				await bot.build_building(UnitTypeId.HYDRALISKDEN)
			else:
				return False
		elif bot.time > 420 and len(bot.structures(UnitTypeId.INFESTATIONPIT)) == 0:
			# build infestation pit
			if bot.can_afford(UnitTypeId.INFESTATIONPIT):
				bot.add_debug_info("make inf pit")
				await bot.build_building(UnitTypeId.INFESTATIONPIT)
			else:
				bot.add_debug_info("can't make infestation pit")
				return False
		elif len(bot.townhalls.ready) < 4:
			bot.add_debug_info("no 4th base")
			return True
		elif bot.time > 420 and len(bot.structures(UnitTypeId.EXTRACTOR)) < 8:
			# build 7th and 8th gas
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_extractor()
			else:
				return False
		elif bot.time > 480 and len(bot.structures(UnitTypeId.HIVE)) + bot.already_pending(UnitTypeId.HIVE) == 0:
			# build hive
			if bot.can_afford(AbilityId.UPGRADETOLAIR_LAIR):
					try: 
						hatch = bot.structures(UnitTypeId.LAIR).ready.idle.random
					except:
						print("no lairs")
					else:
						for ability in await bot.get_available_abilities(hatch):
							if ability == AbilityId.UPGRADETOHIVE_HIVE:
								bot.do(hatch(AbilityId.UPGRADETOHIVE_HIVE))
			else:
				return False

		return True
		
	@staticmethod
	async def make_army(bot):
		if len(bot.structures({UnitTypeId.ROACHWARREN, UnitTypeId.HYDRALISKDEN, UnitTypeId.SPAWNINGPOOL}).ready) == 0:
			return False
		all_larva = bot.units(UnitTypeId.LARVA)
		if len(all_larva) == 0:
			return True
		i = 0
		roaches = (len(bot.units(UnitTypeId.ROACH)) + bot.already_pending(UnitTypeId.ROACH)) / bot.unit_ratio[0]
		hydralisks = (len(bot.units(UnitTypeId.HYDRALISK)) + bot.already_pending(UnitTypeId.HYDRALISK)) / bot.unit_ratio[1]
		
		
		while (i < len(all_larva) and bot.supply_used + 1 + 2 * i <= bot.supply_cap):
			if len(bot.structures(UnitTypeId.HYDRALISKDEN)) > 0:
				if len(bot.structures(UnitTypeId.ROACHWARREN)) > 0:
					if roaches <= hydralisks:
						# make roaches
						if bot.can_afford(UnitTypeId.ROACH):
							bot.do(all_larva[i].train(UnitTypeId.ROACH))
							i += 1
							roaches += 1 / bot.unit_ratio[0]
						else:
							return False
					else:
						# make hydras
						if bot.can_afford(UnitTypeId.HYDRALISK):
							bot.do(all_larva[i].train(UnitTypeId.HYDRALISK))
							i += 1
							hydralisks += 1 / bot.unit_ratio[1]
						else:
							return False
				else:
					# makes hydras
					if bot.can_afford(UnitTypeId.HYDRALISK):
						bot.do(all_larva[i].train(UnitTypeId.HYDRALISK))
						i += 1
						hydralisks += 1 / bot.unit_ratio[1]
					else:
						return False
			elif len(bot.structures(UnitTypeId.ROACHWARREN)) > 0:
				# make roaches
				if bot.can_afford(UnitTypeId.ROACH):
					bot.do(all_larva[i].train(UnitTypeId.ROACH))
					i += 1
					roaches += 2 / bot.unit_ratio[0]
				else:
					return False
			elif roaches + hydralisks == 0:
				if (len(bot.units(UnitTypeId.ZERGLING)) + bot.already_pending(UnitTypeId.ZERGLING)) > 6 and not bot.already_pending(UnitTypeId.ROACHWARREN):
					# make a roach warren
					if bot.can_afford(UnitTypeId.ROACHWARREN):
						await bot.build_building(UnitTypeId.ROACHWARREN)
				# makes lings
				print("panic lings")
				if bot.can_afford(UnitTypeId.ZERGLING):
					bot.do(all_larva[i].train(UnitTypeId.ZERGLING))
					i += 1
				else:
					return False

					
		return True

	@staticmethod
	async def get_upgrades(bot):
		# ovi speed
		if bot.already_pending_upgrade(UpgradeId.OVERLORDSPEED) == 0 and len(bot.structures(UnitTypeId.HATCHERY).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.HATCHERY, UpgradeId.OVERLORDSPEED, AbilityId.RESEARCH_PNEUMATIZEDCARAPACE)
		# +1 ranged, +1 carapace
		if bot.already_pending_upgrade(UpgradeId.ZERGMISSILEWEAPONSLEVEL1) == 0 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.EVOLUTIONCHAMBER, UpgradeId.ZERGMISSILEWEAPONSLEVEL1, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1)
		if bot.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL1) == 0 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.EVOLUTIONCHAMBER, UpgradeId.ZERGGROUNDARMORSLEVEL1, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1)
		# lair
		if len(bot.structures({UnitTypeId.LAIR, UnitTypeId.HIVE}).ready) == 0:
			return True
		# roach speed
		if bot.already_pending_upgrade(UpgradeId.GLIALRECONSTITUTION) == 0 and len(bot.structures(UnitTypeId.ROACHWARREN).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.ROACHWARREN, UpgradeId.GLIALRECONSTITUTION, AbilityId.RESEARCH_GLIALREGENERATION)
		# +2/+2
		if bot.already_pending_upgrade(UpgradeId.ZERGMISSILEWEAPONSLEVEL2) == 0 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.EVOLUTIONCHAMBER, UpgradeId.ZERGMISSILEWEAPONSLEVEL2, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2)
		if bot.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL2) == 0 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.EVOLUTIONCHAMBER, UpgradeId.ZERGGROUNDARMORSLEVEL2, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2)
		# hydra speed
		if bot.already_pending_upgrade(UpgradeId.EVOLVEMUSCULARAUGMENTS) == 0 and len(bot.structures(UnitTypeId.HYDRALISKDEN).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.HYDRALISKDEN, UpgradeId.EVOLVEMUSCULARAUGMENTS, AbilityId.RESEARCH_MUSCULARAUGMENTS)
		# hydra range
		if bot.already_pending_upgrade(UpgradeId.EVOLVEGROOVEDSPINES) == 0 and len(bot.structures(UnitTypeId.HYDRALISKDEN).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.HYDRALISKDEN, UpgradeId.EVOLVEGROOVEDSPINES, AbilityId.RESEARCH_GROOVEDSPINES)
		# burrow
		if bot.already_pending_upgrade(UpgradeId.BURROW) == 0 and len(bot.structures(UnitTypeId.HATCHERY).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.HATCHERY, UpgradeId.BURROW, AbilityId.RESEARCH_BURROW)
		# roach burrowed movement
		if bot.already_pending_upgrade(UpgradeId.TUNNELINGCLAWS) == 0 and len(bot.structures(UnitTypeId.ROACHWARREN).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.ROACHWARREN, UpgradeId.TUNNELINGCLAWS, AbilityId.RESEARCH_TUNNELINGCLAWS)
		# hive
		if len(bot.structures(UnitTypeId.HIVE).ready) == 0:
			return True
		# +3/+3
		if bot.already_pending_upgrade(UpgradeId.ZERGMISSILEWEAPONSLEVEL3) == 0 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.EVOLUTIONCHAMBER, UpgradeId.ZERGMISSILEWEAPONSLEVEL3, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL3)
		if bot.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL3) == 0 and len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready.idle) > 0:
			return bot.get_upgrade(UnitTypeId.EVOLUTIONCHAMBER, UpgradeId.ZERGGROUNDARMORSLEVEL3, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3)
	
		return True
	

class MacroRoachHydra(RoachHydraBase):
	@staticmethod
	def to_string():
		return "RH Macro"
	
	@staticmethod
	def test_conditions(bot):
		value = super(MacroRoachHydra, MacroRoachHydra).test_conditions(bot)
		if bot.threat_level <= 1:
			value += 5
		if bot.difference_in_bases < 1:
			value += 4
		if bot.saturation < 1:
			value += 2
		return value
		
	@staticmethod
	async def execute_plan(bot):
		if await MacroRoachHydra.make_overlords(bot):
			if await MacroRoachHydra.expand_tech(bot):
				if await MacroRoachHydra.make_expansions(bot):
					if await MacroRoachHydra.make_drones(bot):
						await MacroRoachHydra.make_army(bot)
					else:
						bot.add_debug_info("failed to make drones")
				else:
					bot.add_debug_info("failed to make expansions")
			else:
				bot.add_debug_info("failed to expand tech")
		else:
			bot.add_debug_info("failed to make overlords")


class BuildArmyRoachHydra(RoachHydraBase):
	@staticmethod
	def to_string():
		return "RH Army"

	@staticmethod
	def test_conditions(bot):
		value = super(BuildArmyRoachHydra, BuildArmyRoachHydra).test_conditions(bot)
		if bot.threat_level > 1:
			value += 10
		return value

	@staticmethod
	async def execute_plan(bot):
		if await BuildArmyRoachHydra.make_overlords(bot):
			if await BuildArmyRoachHydra.make_army(bot):
				if await BuildArmyRoachHydra.make_drones(bot):
					if await BuildArmyRoachHydra.expand_tech(bot):
						await BuildArmyRoachHydra.make_expansions(bot)
					else:
						bot.add_debug_info("failed to expand tech")
				else:
					bot.add_debug_info("failed to make drones")
			else:
				bot.add_debug_info("failed to make army")
		else:
			bot.add_debug_info("failed to make overlords")
	


class TechRoachHydra(RoachHydraBase):
	@staticmethod
	def to_string():
		return "RH Tech"

	@staticmethod
	def test_conditions(bot):
		value = super(TechRoachHydra, TechRoachHydra).test_conditions(bot)
		if bot.threat_level <= .75:
			value += 5
		if bot.difference_in_bases > 1:
			value += 3
		if bot.saturation >= 1:
			value += 3
		elif bot.saturation < .8:
			value -= 8
		if bot.vespene < 100:
			value -= 10
		

		return value
	
	@staticmethod
	async def execute_plan(bot):
		if await TechRoachHydra.make_overlords(bot):
			if await TechRoachHydra.expand_tech(bot):
				if await TechRoachHydra.make_drones(bot):
					if await TechRoachHydra.make_army(bot):
						await TechRoachHydra.make_expansions(bot)
					else:
						bot.add_debug_info("failed to make army")
				else:
					bot.add_debug_info("failed to make drones")
			else:
				bot.add_debug_info("failed to expand tech")
		else:
			bot.add_debug_info("failed to make overlords")
		
	@staticmethod
	async def expand_tech(bot):
		if not await TechRoachHydra.get_upgrades(bot):
			return False


		if len(bot.structures(UnitTypeId.ROACHWARREN)) == 0:
			# build roach warren
			if bot.can_afford(UnitTypeId.ROACHWARREN):
				await bot.build_building(UnitTypeId.ROACHWARREN)
			else:
				return False
		elif len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER)) < 1:
			# build evo chamber
			if bot.can_afford(UnitTypeId.EVOLUTIONCHAMBER):
				await bot.build_building(UnitTypeId.EVOLUTIONCHAMBER)
			else:
				return False
		elif len(bot.structures(UnitTypeId.EXTRACTOR)) < 2:
			# build 2nd gas
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_extractor()
			else:
				return False
		elif len(bot.structures(UnitTypeId.EVOLUTIONCHAMBER)) < 2:
			# build evo chamber
			if bot.can_afford(UnitTypeId.EVOLUTIONCHAMBER):
				await bot.build_building(UnitTypeId.EVOLUTIONCHAMBER)
			else:
				return False
		elif len(bot.structures(UnitTypeId.EXTRACTOR)) < 3:
			# build 3rd gas
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_extractor()
			else:
				return False
		elif len(bot.structures({UnitTypeId.LAIR, UnitTypeId.HIVE})) + bot.already_pending(UnitTypeId.LAIR) == 0:
			# build lair
			if bot.can_afford(AbilityId.UPGRADETOLAIR_LAIR):
					try: 
						hatch = bot.townhalls.ready.idle.random
					except:
						print("no hatches")
					else:
						for ability in await bot.get_available_abilities(hatch):
							if ability == AbilityId.UPGRADETOLAIR_LAIR:
								bot.do(hatch(AbilityId.UPGRADETOLAIR_LAIR))
			else:
				return False
		elif len(bot.townhalls.ready) < 3:
			bot.add_debug_info("no 3rd base")
			return True
		elif len(bot.structures(UnitTypeId.EXTRACTOR)) < 6:
			# build 4th, 5th and 6th gas
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_extractor()
			else:
				return False
		elif len(bot.structures({UnitTypeId.LAIR, UnitTypeId.HIVE})) == 0:
			bot.add_debug_info("no lair")
			return True
		elif len(bot.structures(UnitTypeId.HYDRALISKDEN)) == 0:
			# build hydra den
			if bot.can_afford(UnitTypeId.HYDRALISKDEN):
				await bot.build_building(UnitTypeId.HYDRALISKDEN)
			else:
				return False
		elif len(bot.structures(UnitTypeId.INFESTATIONPIT)) == 0:
			# build infestation pit
			if bot.can_afford(UnitTypeId.INFESTATIONPIT):
				bot.add_debug_info("make inf pit")
				await bot.build_building(UnitTypeId.INFESTATIONPIT)
			else:
				bot.add_debug_info("can't make infestation pit")
				return False
		elif len(bot.townhalls.ready) < 4:
			bot.add_debug_info("no 4th base")
			return True
		elif len(bot.structures(UnitTypeId.EXTRACTOR)) < 8:
			# build 7th and 8th gas
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_extractor()
			else:
				return False
		elif len(bot.structures(UnitTypeId.HIVE)) + bot.already_pending(UnitTypeId.HIVE) == 0:
			# build hive
			if bot.can_afford(AbilityId.UPGRADETOLAIR_LAIR):
					try: 
						hatch = bot.structures(UnitTypeId.LAIR).ready.idle.random
					except:
						print("no lairs")
					else:
						for ability in await bot.get_available_abilities(hatch):
							if ability == AbilityId.UPGRADETOHIVE_HIVE:
								bot.do(hatch(AbilityId.UPGRADETOHIVE_HIVE))
			else:
				return False
  

class MacroRoachSwarmHost(Plan):
	conditions = []
	
	@staticmethod
	async def use_larva(bot):
		print("used some larva")
	   
	@staticmethod 
	async def make_expansions():
		print("maybe make an expo")
	
	@staticmethod
	async def expand_tech(bot):
		print("expand our tech maybe")
	
	@staticmethod
	async def get_upgrades(bot):
		print("could get some upgrades")
		
		
class BuildArmyRoachSwarmHost(Plan):
	conditions = []
	
	@staticmethod
	async def use_larva(bot):
		print("used some larva")
	 
	@staticmethod   
	async def make_expansions(bot):
		print("maybe make an expo")
	
	@staticmethod
	async def expand_tech(bot):
		print("expand our tech maybe")
	
	@staticmethod
	async def get_upgrades(bot):
		print("could get some upgrades")
		
		
class TechRoachSwarmHost(Plan):
	conditions = []
	
	@staticmethod
	async def use_larva(bot):
		print("used some larva")
	 
	@staticmethod   
	async def make_expansions(bot):
		print("maybe make an expo")
	
	@staticmethod
	async def expand_tech(bot):
		print("expand our tech maybe")
	
	@staticmethod
	async def get_upgrades(bot):
		print("could get some upgrades")
		


class ABCRoachTimingBase(Plan):
	"""
	2:20 3rd bases
	3:30 roach warren
	3:50 2x gas
	4:00 lair
	ovi speed
	41 drones
	4-6 queens
	"""

	@staticmethod
	def test_conditions(bot):
		return 0
	
	@staticmethod
	async def execute_plan(bot):
		await ABCRoachTimingBase.micro(bot)

		if await ABCRoachTimingBase.make_overlords(bot):
			if await ABCRoachTimingBase.make_expansions(bot):
				if await ABCRoachTimingBase.expand_tech(bot):
					if await ABCRoachTimingBase.make_drones(bot):
						await ABCRoachTimingBase.make_army(bot)
	
	@staticmethod
	async def make_expansions(bot):
		if len(bot.townhalls) + bot.already_pending(UnitTypeId.HATCHERY) < 3:
			if bot.minerals >= 300:
				bot.last_expansion_time = bot.time
				expansion_location = await bot.get_next_expansion()
				builder_drone = bot.select_build_worker(expansion_location)
				bot.remove_drone(builder_drone.tag)
				bot.do(builder_drone.build(UnitTypeId.HATCHERY, expansion_location))
			else:
				return False
		return True

	@staticmethod
	async def expand_tech(bot):
		if not await ABCRoachTimingBase.get_upgrades(bot):
			return False
		
		if bot.time > 210 and len(bot.structures(UnitTypeId.ROACHWARREN)) < 1:
			# build roach warren
			if bot.can_afford(UnitTypeId.ROACHWARREN):
				await bot.build_building(UnitTypeId.ROACHWARREN)
			else:
				return False
		elif bot.time > 230 and len(bot.structures(UnitTypeId.EXTRACTOR)) < 3:
			# build gas 2 and 3
			if bot.can_afford(UnitTypeId.EXTRACTOR):
				await bot.build_building(UnitTypeId.EXTRACTOR)
			else:
				return False
		elif bot.time > 240 and len(bot.structures({UnitTypeId.LAIR, UnitTypeId.HIVE})) + bot.already_pending(UnitTypeId.LAIR) == 0:
			# build lair
			if bot.can_afford(AbilityId.UPGRADETOLAIR_LAIR):
					try: 
						hatch = bot.townhalls.ready.idle.random
					except:
						print("no hatches")
					else:
						for ability in await bot.get_available_abilities(hatch):
							if ability == AbilityId.UPGRADETOLAIR_LAIR:
								bot.do(hatch(AbilityId.UPGRADETOLAIR_LAIR))
			else:
				return False

	@staticmethod
	async def make_drones(bot):
		# Queens
		queen_need = 6
		if len(bot.units(UnitTypeId.QUEEN)) + bot.already_pending(UnitTypeId.QUEEN) < queen_need and bot.supply_used + 2 <= bot.supply_cap and len(bot.townhalls.ready.idle) > 0:
			if bot.minerals >= 150:
				await bot.build_queen()
				f = open("queen_times.txt", "a")
				f.write("Current Queens: " + str(len(bot.units(UnitTypeId.QUEEN)) + bot.already_pending(UnitTypeId.QUEEN)) + " Queen need: " + str(queen_need) + " Time: " + bot.time_formatted + "\n")
				f.close()
			else:
				return False
			
		# Larva
		all_larva = bot.units(UnitTypeId.LARVA)
		if len(all_larva) == 0:
			return True
		i = 0
		drone_need = 41
		while (i < len(all_larva) and bot.supply_workers + bot.already_pending(UnitTypeId.DRONE) < drone_need and bot.supply_used + 1 + i <= bot.supply_cap):
			if bot.minerals >= 50:
				bot.do(all_larva[i].train(UnitTypeId.DRONE))
				g = open("drone_times.txt", "a")
				g.write("Larva #" + str(i) + " Current Drones: " + str(bot.supply_workers + bot.already_pending(UnitTypeId.DRONE)) + " Drone need: " + str(drone_need) + " Time: " + bot.time_formatted + "\n")
				g.close()            
				drone_need -= 1
				i += 1
			else:
				return False
		return True

	@staticmethod
	async def make_army(bot):
		if len(bot.structures(UnitTypeId.SPAWNINGPOOL).ready) == 0:
			return False
		all_larva = bot.units(UnitTypeId.LARVA)
		if len(all_larva) == 0:
			return True
		i = 0
		lings = (len(bot.units(UnitTypeId.ZERGLING)) + bot.already_pending(UnitTypeId.ZERGLING))
		ling_need = math.inf
		if bot.time < 330:
			ling_need = 6
		roaches = (len(bot.units(UnitTypeId.ROACH)) + bot.already_pending(UnitTypeId.ROACH))
		roach_need = 2
		if bot.time < 330:
			roach_need = 8
		#ravagers = (len(bot.units(UnitTypeId.RAVAGER)) + bot.already_pending(UnitTypeId.RAVAGER))
		
		while (i < len(all_larva) and bot.supply_used + 1 + i <= bot.supply_cap):
			if len(bot.structures(UnitTypeId.ROACHWARREN)) > 0 and roaches < roach_need and bot.vespene >= 25:
				if bot.can_afford(UnitTypeId.ROACH):
					bot.do(all_larva[i].train(UnitTypeId.ROACH))
					i += 1
					roaches += 1
				else:
					return False
			elif lings < ling_need:
				if bot.can_afford(UnitTypeId.ZERGLING):
					bot.do(all_larva[i].train(UnitTypeId.ZERGLING))
					i += 1
					lings += 2
				else:
					return False
		
		for roach in bot.units(UnitTypeId.ROACH).ready:
			if bot.vespene >= 75:
				if bot.can_afford(UnitTypeId.RAVAGER):
					bot.do(roach(AbilityId.MORPHTORAVAGER_RAVAGER))
				else:
					return False

		# dropperlords
		dropperlord_need = 2
		if len(bot.units(UnitTypeId.OVERLORDTRANSPORT)) < dropperlord_need:
			if bot.can_afford(AbilityId.MORPH_OVERLORDTRANSPORT):
				bot.make_dropperlord()
			else:
				return False

		return True


class ABCRoachTimingPrep(ABCRoachTimingBase):
	
	@staticmethod
	def test_conditions(bot):
		value = super(ABCRoachTimingPrep, ABCRoachTimingPrep).test_conditions(bot)
		if bot.time < 330:
			value += 5
		else:
			value -= 5
		return value
		
class ABCRoachTimingAttacking(ABCRoachTimingBase):

	@staticmethod
	def test_conditions(bot):
		value = super(ABCRoachTimingAttacking, ABCRoachTimingAttacking).test_conditions(bot)
		if bot.time > 330:
			value += 5
		else:
			value -= 5
		return value



class AntiProxyRax(Plan):
	conditions = []
	
	@staticmethod
	async def use_larva(bot):
		print("used some larva")
		
	@staticmethod
	async def make_expansions(bot):
		print("maybe make an expo")
	
	@staticmethod
	async def expand_tech(bot):
		print("expand our tech maybe")
	
	@staticmethod
	async def get_upgrades(bot):
		print("could get some upgrades")
		
		
all_builds = [MacroLingBaneHydra,
			BuildArmyLingBaneHydra,
			TechLingBaneHydra,
			MacroRoachHydra,
			BuildArmyRoachHydra,
			TechRoachHydra,
			MacroRoachSwarmHost,
			BuildArmyRoachSwarmHost,
			TechRoachSwarmHost,
			AntiProxyRax]