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
        bot.add_debug_info("help")
        # Make Overlords
        all_larva = bot.units(UnitTypeId.LARVA)
        if len(all_larva) == 0:
            return True
        i = 0
        while (i < len(all_larva) and bot.supply_cap < 200 and
               ((bot.supply_used / bot.supply_cap >= .8 and not bot.already_pending(UnitTypeId.OVERLORD) > 0) or 
                (bot.supply_used / bot.supply_cap >= .9 and not bot.already_pending(UnitTypeId.OVERLORD) > 1))):
            if bot.minerals >= 100:
                bot.do(all_larva[i].train(UnitTypeId.OVERLORD))
                f = open("overlord_times.txt", "a")
                f.write("Larva #" + str(i) + " Overlord #" + str(len(bot.units(UnitTypeId.OVERLORD)) + 1) + " Supply used: " + str(bot.supply_used) + " Supply cap: " + str(bot.supply_cap) + " Time: " + bot.time_formatted + "\n")
                f.close()
                i += 1
            else:
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
        
    
    
class MacroLingBaneHydra(LingBaneHydraBase):
    @staticmethod
    def to_string():
        return "LBH Macro"
    
    @staticmethod
    def test_conditions(bot):
        value = super(MacroLingBaneHydra, MacroLingBaneHydra).test_conditions(bot)
        if bot.get_threat_level() <= 1:
            value += 5
        if bot.get_difference_in_bases() < 1:
            value += 2
        if bot.get_saturation() < 1:
            value += 2
        return value
    
    @staticmethod
    async def execute_plan(bot):
        if await MacroLingBaneHydra.make_overlords(bot):
            if await MacroLingBaneHydra.make_expansions(bot):
                if await MacroLingBaneHydra.make_drones(bot):
                    if await MacroLingBaneHydra.expand_tech(bot):
                        await MacroLingBaneHydra.make_army(bot)

    
    @staticmethod
    async def expand_tech(bot):
        
        if not await MacroLingBaneHydra.get_upgrades(bot):
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
                await bot.build_building(UnitTypeId.BANELING)
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
        elif bot.time > 350 and len(bot.structures(UnitTypeId.EXTRACTOR)) < 5:
            # build 5th extractor
            if bot.can_afford(UnitTypeId.EXTRACTOR):
                await bot.build_extractor()
            else:
                return False
        elif bot.time > 480 and len(bot.structures(UnitTypeId.INFESTATIONPIT)) == 0:
            # build infestation pit
            if bot.can_afford(UnitTypeId.INFESTATIONPIT):
                await bot.build_building(UnitTypeId.INFESTATIONPIT)
            else:
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

    
    @staticmethod
    async def get_upgrades(bot):
        return True    
    
    

class BuildArmyLingBaneHydra(LingBaneHydraBase):
    @staticmethod
    def to_string():
        return "LBH Army"

    @staticmethod
    def test_conditions(bot):
        value = super(MacroLingBaneHydra, MacroLingBaneHydra).test_conditions(bot)
        if bot.get_threat_level() > 1:
            value += 10
        return value

    @staticmethod
    async def execute_plan(bot):
        if await BuildArmyLingBaneHydra.make_overlords(bot):
            if await BuildArmyLingBaneHydra.make_army(bot):
                if await BuildArmyLingBaneHydra.make_drones(bot):
                    if await BuildArmyLingBaneHydra.expand_tech(bot):
                        await BuildArmyLingBaneHydra.make_expansions(bot)

    
    @staticmethod
    async def get_upgrades(bot):
        return True
        
        
class TechLingBaneHydra(LingBaneHydraBase):
    @staticmethod
    def to_string():
        return "LBH Tech"

    @staticmethod
    def test_conditions(bot):
        value = super(MacroLingBaneHydra, MacroLingBaneHydra).test_conditions(bot)
        if bot.get_threat_level() <= .75:
            value += 5
        if bot.get_difference_in_bases() > 1:
            value += 3
        if bot.get_saturation() >= 1:
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
    
    @staticmethod
    async def get_upgrades(bot):
        bot.add_debug_info("could get some upgrades")
        return True
        
        
class MacroRoachHydra(Plan):
    conditions = []
    
    async def use_larva(bot):
        print("used some larva")
        
    async def make_expansions(bot):
        print("maybe make an expo")
    
    async def expand_tech(bot):
        print("expand our tech maybe")
    
    async def get_upgrades(bot):
        print("could get some upgrades")
        
        
class BuildArmyRoachHydra(Plan):
    conditions = []
    
    async def use_larva(bot):
        print("used some larva")
        
    async def make_expansions(bot):
        print("maybe make an expo")
    
    async def expand_tech(bot):
        print("expand our tech maybe")
    
    async def get_upgrades(bot):
        print("could get some upgrades")
        
        
class TechRoachHydra(Plan):
    conditions = []
    
    async def use_larva(bot):
        print("used some larva")
        
    async def make_expansions(bot):
        print("maybe make an expo")
    
    async def expand_tech(bot):
        print("expand our tech maybe")
    
    async def get_upgrades(bot):
        print("could get some upgrades")
        
        
class MacroRoachSwarmHost(Plan):
    conditions = []
    
    async def use_larva(bot):
        print("used some larva")
        
    async def make_expansions():
        print("maybe make an expo")
    
    async def expand_tech(bot):
        print("expand our tech maybe")
    
    async def get_upgrades(bot):
        print("could get some upgrades")
        
        
class BuildArmyRoachSwarmHost(Plan):
    conditions = []
    
    async def use_larva(bot):
        print("used some larva")
        
    async def make_expansions(bot):
        print("maybe make an expo")
    
    async def expand_tech(bot):
        print("expand our tech maybe")
    
    async def get_upgrades(bot):
        print("could get some upgrades")
        
        
class TechRoachSwarmHost(Plan):
    conditions = []
    
    async def use_larva(bot):
        print("used some larva")
        
    async def make_expansions(bot):
        print("maybe make an expo")
    
    async def expand_tech(bot):
        print("expand our tech maybe")
    
    async def get_upgrades(bot):
        print("could get some upgrades")
        
        
class AntiProxyRax(Plan):
    conditions = []
    
    async def use_larva(bot):
        print("used some larva")
        
    async def make_expansions(bot):
        print("maybe make an expo")
    
    async def expand_tech(bot):
        print("expand our tech maybe")
    
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