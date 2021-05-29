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


class Plan:
    conditions = []
    
    async def use_larva(bot):
        # Make Overlords
        all_larva = bot.units(UnitTypeId.LARVA)
        if len(all_larva) == 0:
            return
        i = 0
        while (i < len(all_larva) and bot.supply_cap < 200 and bot.minerals >= 100 and
               ((bot.supply_used / bot.supply_cap >= .8 and not bot.already_pending(UnitTypeId.OVERLORD) > 0) or 
                (bot.supply_used / bot.supply_cap >= .9 and not bot.already_pending(UnitTypeId.OVERLORD) > 1))):
            bot.do(all_larva[i].train(UnitTypeId.OVERLORD))
            f = open("overlord_times.txt", "a")
            f.write("Larva #" + str(i) + " Overlord #" + str(len(bot.units(UnitTypeId.OVERLORD)) + 1) + " Supply used: " + str(bot.supply_used) + " Supply cap: " + str(bot.supply_cap) + " Time: " + bot.time_formatted + "\n")
            f.close()
            i += 1
    
    async def make_expansions(bot):
        print("Error make_expansions called on Plan class")
    
    async def expand_tech(bot):
        print("Error expand_tech called on Plan class")
    
    async def get_upgrades(bot):
        print("Error get_upgrades called on Plan class")
    
    
class MacroLingBaneHydra(Plan):
    conditions = []
    
    async def use_larva(bot):
        await super(MacroLingBaneHydra, MacroLingBaneHydra).use_larva(bot)
        
        if (bot.supply_cap < 200 and ((bot.supply_used / bot.supply_cap >= .8 and not bot.already_pending(UnitTypeId.OVERLORD) > 0) or 
             (bot.supply_used / bot.supply_cap >= .9 and not bot.already_pending(UnitTypeId.OVERLORD) > 1))):
            # save up to build an overlord
            return
            
        # Queens
        queen_need = min(8, len(bot.townhalls.ready) * 2 + 2)
        if bot.minerals >= 150 and len(bot.units(UnitTypeId.QUEEN)) + bot.already_pending(UnitTypeId.QUEEN) < queen_need and bot.supply_used + 2 <= bot.supply_cap and len(bot.townhalls.ready.idle) > 0:
            await bot.build_queen()
            f = open("queen_times.txt", "a")
            f.write("Current Queens: " + str(len(bot.units(UnitTypeId.QUEEN)) + bot.already_pending(UnitTypeId.QUEEN)) + " Queen need: " + str(queen_need) + " Time: " + bot.time_formatted + "\n")
            f.close()
            
        # Larva
        all_larva = bot.units(UnitTypeId.LARVA)
        if len(all_larva) == 0:
            return
        i = 0
        drone_need = min(80, len(bot.townhalls) * 16 + len(bot.structures(UnitTypeId.EXTRACTOR)) * 3)
        while (i < len(all_larva) and bot.supply_workers + bot.already_pending(UnitTypeId.DRONE) < drone_need and bot.supply_used + 1 + i <= bot.supply_cap and bot.minerals >= 50):
            bot.do(all_larva[i].train(UnitTypeId.DRONE))
            g = open("drone_times.txt", "a")
            g.write("Larva #" + str(i) + " Current Drones: " + str(bot.supply_workers + bot.already_pending(UnitTypeId.DRONE)) + " Drone need: " + str(drone_need) + " Time: " + bot.time_formatted + "\n")
            g.close()            
            drone_need -= 1
            i += 1
        
        
    async def make_expansions(bot):
        if bot.minerals >= 300 and sum(bot.enemy_expos) + 1 >= len(bot.townhalls) + bot.already_pending(UnitTypeId.HATCHERY):
            bot.last_expansion_time = bot.time
            expansion_location = await bot.get_next_expansion()
            builder_drone = bot.select_build_worker(expansion_location)
            bot.remove_drone(builder_drone.tag)
            bot.do(builder_drone.build(UnitTypeId.HATCHERY, expansion_location))
    
    async def expand_tech(bot):
        print("expand our tech maybe")
        # 4:00 - evo
        # finished evo - +1 melee
        # 5:00 - lair
        # 5:10 - bane nest
        # lair and bane nest - bane speed
        # lair - hydra den
        # hydra den - both hydra upgrades
        # +1 melee - +2 melee
        
        
    
    async def get_upgrades(bot):
        print("could get some upgrades")

class BuildArmyLingBaneHydra(Plan):
    conditions = []
    
    async def use_larva(bot):
        print("used some larva")
        
    async def make_expansions(bot):
        print("maybe make an expo")
    
    async def expand_tech(bot):
        print("expand our tech maybe")
    
    async def get_upgrades(bot):
        print("could get some upgrades")
        
        
class TechLingBaneHydra(Plan):
    conditions = []
    
    async def use_larva(bot):
        print("used some larva")
        
    async def make_expansions(bot):
        print("maybe make an expo")
    
    async def expand_tech(bot):
        print("expand our tech maybe")
    
    async def get_upgrades(bot):
        print("could get some upgrades")
        
        
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