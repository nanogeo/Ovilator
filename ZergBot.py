# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 23:53:47 2020

@author: hocke
"""

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
from sc2.constants import EGG, DRONE, QUEEN, ZERGLING, BANELING, ROACH, RAVAGER, HYDRALISK, LURKER, MUTALISK, CORRUPTOR, BROODLORD, OVERLORD, OVERSEER, INFESTOR, SWARMHOSTMP, LARVA, VIPER, ULTRALISK, LOCUSTMP, LOCUSTMPFLYING
from sc2.constants import ROACHBURROWED
from sc2.constants import HATCHERY, LAIR, HIVE, EXTRACTOR, SPAWNINGPOOL, ROACHWARREN, HYDRALISKDEN, LURKERDEN, SPIRE, GREATERSPIRE, EVOLUTIONCHAMBER, SPORECRAWLER, SPINECRAWLER, INFESTATIONPIT, BANELINGNEST, CREEPTUMOR, NYDUSNETWORK, NYDUSCANAL, ULTRALISKCAVERN, CREEPTUMORBURROWED, CREEPTUMORQUEEN
from sc2.constants import PROBE, ZEALOT, STALKER, SENTRY, ADEPT, HIGHTEMPLAR, DARKTEMPLAR, IMMORTAL, COLOSSUS, DISRUPTOR, ARCHON, OBSERVER, WARPPRISM, PHOENIX, VOIDRAY, ORACLE, CARRIER, TEMPEST, MOTHERSHIP
from sc2.constants import SCV, MULE, MARINE, MARAUDER, REAPER, GHOST, HELLION, SIEGETANK, CYCLONE, THOR, VIKING, MEDIVAC, LIBERATOR, RAVEN, BANSHEE, BATTLECRUISER
from sc2.constants import NEXUS, PYLON, ASSIMILATOR, GATEWAY, FORGE, CYBERNETICSCORE, PHOTONCANNON, SHIELDBATTERY, ROBOTICSFACILITY, WARPGATE, STARGATE, TWILIGHTCOUNCIL, ROBOTICSBAY, FLEETBEACON, TEMPLARARCHIVE, DARKSHRINE
from sc2.constants import COMMANDCENTER, ORBITALCOMMAND, PLANETARYFORTRESS, SUPPLYDEPOT, REFINERY, BARRACKS, ENGINEERINGBAY, BUNKER, SENSORTOWER, MISSILETURRET, FACTORY, GHOSTACADEMY, STARPORT, ARMORY, FUSIONCORE
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.buff_id import BuffId
from s2clientprotocol import raw_pb2 as raw_pb
from s2clientprotocol import sc2api_pb2 as sc_pb

from dijkstra import Graph
from dijkstra import DijkstraSPF
import random
import math
from enum import Enum

import Plans

class EnemyPlan:
    MACRO = 1
    TURTLE = 2
    TECHING = 3
    TIMING_ATTACK = 4
    ALL_IN = 5
    CHEESE = 6

class ArmyComp:
    LING_BANE_HYDRA = 1
    ROACH_HYDRA = 2
    LING_BANE_MUTA = 3
    ROACH_SWARM_HOST = 4

class ArmyState:
    CONSOLIDATING = 1
    RALLYING = 2
    ATTACKING = 3
    PROTECTING = 4

class EnemyArmyState:
    DEFENDING = 1
    PREPARING_ATTACK = 2
    MOVING_TO_ATTACK = 3
    
class MutaGroupState:
    CONSOLIDATING = 1
    MOVING_TO_RALLY = 2
    MOVING_TO_ATTACK = 3
    ATTACKING = 4
    RETREATING = 5
    
class SwarmHostState:
    WAITING = 1
    UNLOADING = 2

class QueenState:
    SPREAD_CREEP = 1
    DEFEND = 2
    SPREAD_CAREFULLY = 3
    
class LingRunby:
    ling_tags = []
    path = []
    target = None
    
class ProxyStatus(Enum):
    NONE = 1
    PR_RAX_STARTED = 10
    PR_SOME_RAX_FINISHED = 11
    PR_ALL_RAX_FINISHED = 12
    PR_UNPROTECTED_BUNKER = 13
    PR_PROTECTED_BUNKER = 14
    PR_NO_BUNKER_ATTACK = 15
    PR_BUNKER_FINISHED = 16
    
class MinerStatus(Enum):
    MOVING_TO_HATCH = 1
    MOVING_TO_MINERALS = 2
    MINING = 3




class BlankBot(sc2.BotAI):
    def __init__(self):
        self.i = True
    
    async def on_step(self, iteration):
        self.i = False
    

class ZergBot(sc2.BotAI):
    def __init__(self):
        self.unit_command_uses_self_do = True
        self.raw_affects_selection = True
        
        self.current_plan = Plans.MacroLingBaneHydra
        self.has_debug = False
        self.debug_interval = 10
        self.unit_command_uses_self_do = True
        self.bases = []
        self.injecting_queens = []
        self.creep_queens = []
        self.inactive_creep_tumors = []
        self.current_plan = Plans.MacroLingBaneHydra
        self.build_order = [(0, self.build_drone),
                            (10, self.build_overlord),
                            (14, self.build_drone),
                            (28, self.build_drone),
                            (28, self.build_drone),
                            (34, self.build_pool),
                            (41, self.build_drone),
                            (45, self.build_drone),
                            (55, self.build_hatch),
                            (68, self.build_drone),
                            (86, self.build_ling),
                            (86, self.build_ling),
                            (86, self.build_ling),
                            (87, self.build_gas),
                            (89, self.build_queen),
                            (96, self.build_overlord),
                            (103, self.send_ling_scouts),
                            (106, self.build_drone),
                            (116, self.build_drone)]
        """
        [(0, self.build_drone),
        (12, self.build_overlord),
        (16, self.build_drone),
        (30, self.build_drone),
        (30, self.build_drone),
        (37, self.build_pool),
        (44, self.build_drone),
        (50, self.build_drone),
        (72, self.build_hatch),
        (74, self.build_drone),
        (87, self.build_ling),
        (87, self.build_ling),
        (87, self.build_ling),
        (93, self.build_queen),
        (95, self.build_gas),
        (101, self.build_overlord),
        (106, self.send_ling_scouts),
        (109, self.build_drone),
        (120, self.build_drone)]
        
        
        (42, 92),	#	enemy natural pillar
        (122, 78),	#	natural enterance pillar
        # scouting
        (64, 147),	#	near enemy main
        (24, 147),	#	behind enemy main
        (24, 85),	#	enemy natural deadspace
        (25, 54),	#	enemy inline 3rd space
        # enemy bases
        (46, 71),	#	enemy inline 3rd
        (70, 103),	#	enemy triangle 3rd enemy natural exit 2
        (42, 35),	#	enemy inline 4th
        (86, 126),	#	enemy 5th base
        (40, 60),	#	enemy inline 3rd pillar - move to  10
        # early attacks
        (62, 86),	#	enemy natural exit pillar
        (49, 57),	#	enemy inline 3rd exit
        (100, 114),	#	close right route pillar
        (60, 56),	#	enemy inline 3rd exit pillar
        (69, 73),	#	enemy natural exit
        # attack paths
        (107, 124),	#	far right route
        (81, 64),	#	close left route
        (78, 84),	#	middle route
        (90, 104),	#	close right route
        (74, 38),	#	farth left route  20
        (90, 90),	#	right middle route pillar - replace
        (94, 74),	#	left middle route pillar - replace
        (120, 130),	#	far right route pillar - add
        # deadspace
        (159, 81),	#	close deadspace
        (119, 19),	#	close opposite deadspace
        (159, 112),	#	far deadspace
        (77, 19),	#	far opposite deadspace
        (153, 143),	#	right corner
        (31, 22), 	#	left corner
        (106, 146),	#	far right deadspace  30
        # defensive
        (144, 104),	#	inline 3rd pillar
        (84, 50),	#	close left route pillar
        (105, 95),	#	close right route 2
        (64, 34),	#	farthest left route pillar
        (124, 108),	#	3rd base exit pillar
        # special
        (58, 119)	#	elevator
        """
        
        self.tag_to_unit = {} # {unit_tag : unit} updated each iteration
        self.add_new_base = None
        
        self.overlord_positions = [ (42, 92),	#	enemy natural pillar
                                    (122, 78),	#	natural enterance pillar
                                    (64, 147),	#	near enemy main
                                    (62, 86),	#	enemy natural exit pillar
                                    (46, 71),	#	enemy inline 3rd
                                    (70, 103),	#	enemy triangle 3rd enemy natural exit 2
                                    (24, 85),	#	enemy natural deadspace
                                    (69, 73),	#	enemy natural exit
                                    (84, 50),	#	close left route pillar
                                    (105, 95),	#	close right route 2
                                    (24, 147),	#	behind enemy main
                                    (86, 126),	#	enemy 5th base
                                    (159, 81),	#	close deadspace
                                    (119, 19),	#	close opposite deadspace
                                    (100, 114),	#	close right route pillar
                                    (90, 90),	#	right middle route pillar - replace
                                    (94, 74),	#	left middle route pillar - replace
                                    (64, 34),	#	farthest left route pillar
                                    (40, 60),	#	enemy inline 3rd pillar - move to
                                    (42, 35),	#	enemy inline 4th
                                    (60, 56),	#	enemy inline 3rd exit pillar
                                    (77, 19),	#	far opposite deadspace
                                    (106, 146),	#	far right deadspace
                                    (120, 130),	#	far right route pillar - add
                                    (159, 112),	#	far deadspace
                                    (25, 54),	#	enemy inline 3rd space
                                    (153, 143),	#	right corner
                                    (31, 22), 	#	left corner
                                    (60, 56),	#	enemy inline 3rd exit pillar
                                    (58, 119)	#	elevator
                                    ]
        self.expos = [(143.5, 32.5),    # BR main
                    (148.5, 125.5),     # BR inline 5th
                    (79.5, 136.5),      # TL triangle 5th
                    (36.5, 69.5),       # TL inline 3rd
                    (59.5, 43.5),       # TL middle
                    (119.5, 53.5),      # BR triangle 3rd
                    (35.5, 38.5),       # TL inline 5th
                    (38.5, 102.5),      # TL natural
                    (124.5, 120.5),     # BR middle
                    (64.5, 110.5),      # TL triangle 3rd
                    (145.5, 61.5),      # BR natural
                    (147.5, 94.5),      # BR inline 3rd
                    (104.5, 27.5),      # BR triangle 5th
                    (40.5, 131.5)       # TL main
                    ]
        
        self.last_expansion_time = 0
        self.enemy_expos = [0, 0, 0, 0, 0, 0]
        self.main_scout_path = [(53, 133), (50, 125), (36, 125), (37, 137)]
        self.scouts_sent = 0
        self.army_req = 0
        self.drone_req = 0
        self.ovi_to_position_dict = {}
        self.position_to_ovi_dict  = {}
        self.build_step = 0
        self.builder_drone = None
        self.build_location = None
        self.spore_positions = [(123, 54),
                                (155, 120),
                                (155, 132),
                                (119, 46),
                                (104, 20),
                                (152, 68),
                                (152, 33),
                                (142, 25),
                                (152, 88),
                                (152, 101),
                                (113, 28),
                                (151, 56)]
# creep
        self.creep_locations = [(139.618896484375, 92.466552734375),
                                (127.156982421875, 81.634765625),
                                (129.79638671875, 64.93896484375),
                                (141.262451171875, 42.2890625),
                                (114.623291015625, 65.232421875),
                                (139.1455078125, 65.218017578125)]
        self.creep_spread_to = []
        self.updated_creep = False
        self.creep_queen_state = QueenState.SPREAD_CREEP
        self.creep_coverage = 0
        
        self.drone_need = 0
        self.queen_need = 0
        self.zergling_need = 0
        self.baneling_need = 0
        self.roach_need = 0
        self.ravager_need = 0
        self.hydralisk_need = 0
        self.lurker_need = 0
        self.mutalisk_need = 0
        self.corrupter_need = 0
        self.broodlord_need = 0
        self.infestor_need = 0
        self.swarmhost_need = 0
        self.viper_need = 0
        self.ultralisk_need = 0
        
        self.expansion_need = 0
        self.extractor_need = 0
        self.baneling_nest_need = 0
        self.roach_warren_need = 0
        self.hydra_den_need = 0
        self.lurker_den_need = 0
        self.spire_need = 0
        self.greater_spire_need = 0
        self.ultralisk_cavern_need = 0
        self.evo_chamber_need = 0
        self.lair_need = 0
        self.infestation_pit_need = 0
        self.hive_need = 0
        
        self.pending_upgrade = False
        
        self.enemy_unit_tags = {}
        self.enemy_unit_numbers = {}
        self.enemy_army_position = None
        self.enemy_attack_point = None

# mining
        
        self.mineral_patches = {} # {tag : (is_close, drone1, drone2, drone3)}
        self.mineral_patches_reversed = {} # {drone_tag : (mineral_tag, drop_off_point, pick_up_point)}
        self.extractors = {} # {tag : (drone1, drone2, drone3)}
        self.extractors_reversed = {} # {drone_tag : (mineral_tag, drop_off_point, pick_up_point)}
        self.mining_drone_tags = []
        self.non_mining_drone_tags = []
        

# scouting
        self.zergling_scout_tags = [None]*6
        self.last_ling_scout_time = 0
        self.enemy_army_state = EnemyArmyState.DEFENDING
        self.proxy_location = None
        """[(108, 81),0
            (51, 57),1
            (149, 95),2
            (64, 107),3
            (36, 69),4
            (78, 83),5
            (55, 23),6
            (118, 92),7
            (35, 38),8
            (128, 122),9
            (105, 28),10
            (72, 96),11
            (91, 97),12
            (105, 109),13
            (77, 54),14
            (150, 126),15
            (81, 136),16
            (75, 32),17
            (113, 118),18
            (66, 69),19
            (129, 141),20
            (92, 67)]21"""
        self.scouting_path = [[(105, 28), (75, 32), (55, 23), (35, 38), (36, 69)],
                               [(108, 81), (75, 32), (51, 57), (66, 69)],
                               [(77, 54), (92, 67), (78, 83)],
                               [(91, 97), (105, 109), (72, 96)],
                               [(118, 92), (128, 122), (113, 118), (64, 107)],
                               [(149, 95), (150, 126), (129, 141), (81, 136)]]
        
# proxy stuff
        self.proxy_status = ProxyStatus.NONE
        self.proxy_buildings = [] # (tag, type_id, build progress)
        self.proxy_units = [] # (tag, type_id, health)
        self.pulled_worker_tags = []
        self.breaking_proxy = False
        self.proxy_finished_time = 0
        
# army stuff
        self.rally_points = [(114, 131),
                            (84, 117),
                            (40, 70),
                            (68, 68),
                            (101, 106),
                            (60, 46),
                            (93, 123),
                            (80, 81)]
        self.army_positions = [Point2((132, 78)),
                                Point2((119, 94)),
                                Point2((146, 94)),
                                Point2((132, 141)),
                                Point2((54, 23)),
                                Point2((92, 125)),
                                Point2((72, 97)),
                                Point2((125, 119)),
                                Point2((111, 63)),
                                Point2((97, 48)),
                                Point2((82, 113)),
                                Point2((86, 61)),
                                Point2((34, 39)),
                                Point2((112, 129)),
                                Point2((50, 57)),
                                Point2((106, 81)),
                                Point2((99, 104)),
                                Point2((66, 72)),
                                Point2((150, 127)),
                                Point2((79, 82)),
                                Point2((73, 35)),
                                Point2((134, 106)),
                                Point2((61, 44)),
                                Point2((91, 33))]
        self.army_position_links = [[1, 2],
                                    [0, 15, 16, 21],
                                    [0, 21],
                                    [13, 18],
                                    [12, 20],
                                    [10, 13, 16],
                                    [10, 17, 19],
                                    [13, 21],
                                    [9, 15],
                                    [8, 11, 23],
                                    [5, 6],
                                    [9, 17, 19],
                                    [4, 14],
                                    [3, 5, 7],
                                    [12, 17, 22],
                                    [1, 8, 16, 19],
                                    [1, 5, 10, 15],
                                    [6, 11, 14, 19],
                                    [3, 21],
                                    [6, 11, 15, 17],
                                    [4, 22, 23],
                                    [1, 2, 7, 18],
                                    [14, 20],
                                    [9, 20]]
        self.defense_points = [[2, 5, 6, 7],    # nat
                               [7, 14],         # inline 3rd
                               [2, 5],          # tri 3rd
                               [10, 13],        # inline 5th
                               [5, 9],          # tri 5th
                               [0]]             # middle
        self.map_graph = Graph()
        self.army_spot = (127, 81)
        self.attack_position = None
        self.rally_point = None
        self.army_unit_tags = []
        
        self.burrow_researched = False
        self.burrow_movement_researched = False
        self.army_state = ArmyState.CONSOLIDATING
        
        self.army_composition = ArmyComp.LING_BANE_HYDRA
        

# muta micro
        self.muta_attack_positions = [(57, 41),
                                    (35, 102),
                                    (61, 113),
                                    (32, 69),
                                    (32, 38),
                                    (76, 139),
                                    (37, 134)]
        self.muta_rally_points = [(24, 16),
                                (106, 148),
                                (24, 86),
                                (63, 129),
                                (64, 148),
                                (24, 54),
                                (76, 16),
                                (24, 148),
                                (24, 116)]
        self.muta_group_tags = []
        self.muta_group_state = MutaGroupState.CONSOLIDATING
        self.muta_rally_point_attack = None
        self.muta_rally_point_retreat = None
        self.muta_attack_point = None
        
# swarm hosts
        self.nydus_positions = [(30.5, 77.5),
                                (75.5, 130.5),
                                (103.5, 111.5),
                                (33.5, 48.5),
                                (109.5, 135.5),
                                (57.5, 44.5),
                                (83.5, 85.5),
                                (60.5, 132.5),
                                (42.5, 141.5),
                                (46.5, 23.5),
                                (88.5, 98.5),
                                (74.5, 55.5)]
        self.last_locust_wave = 0
        self.swarm_host_state = SwarmHostState.WAITING
        self.swarm_host_nydus = None
    
    
    async def on_start(self):
        self.client.game_step: int = 2
        self.set_up_map_graph()
    
    async def on_step(self, iteration):
        self.update_unit_tags()
        if iteration == 1:
            self.split_drones()
        if self.add_new_base != None:
            for mineral_field in self.all_units.mineral_field.closer_than(10, self.tag_to_unit[self.add_new_base].position):
                if mineral_field.is_snapshot:
                    break
                self.mineral_patches[mineral_field.tag] = (mineral_field.mineral_contents == 1800, None, None, None)
                self.add_new_base = None
        await self.display_debug_info()
        await self.distribute_workers()
        await self.execute_build()
        await self.get_upgrades()
        await self.inject_larva()
        await self.update_creep()
        await self.spread_creep()
        await self.position_overlords()
        await self.scouting()
        await self.update_enemy_units()
        await self.track_enemy_army_position()
        if self.build_step >= len(self.build_order):
            await self.current_plan.use_larva(self)
            await self.current_plan.make_expansions(self)
            #await self.current_plan.expand_tech(self)
            #await self.current_plan.get_upgrades(self)
            
            await self.update_building_need()
            #await self.use_larva()
            #await self.make_expansions()
            await self.expand_tech()
            await self.scout_with_lings()
            await self.micro()
            

########################################
############# BUILD ORDER ##############
########################################
            
    async def execute_build(self):
        if self.build_step < len(self.build_order):
            if self.time >= self.build_order[self.build_step][0]:
                action = self.build_order[self.build_step][1]
                if await action():
                    self.build_step += 1

    async def build_drone(self):
        if self.minerals >= 50 and self.supply_left >= 1 and len(self.units(LARVA)) > 0:
            self.do(self.units(LARVA).random.train(DRONE))
            return True
        return False
    
    async def build_overlord(self):
        if self.minerals >= 100 and len(self.units(LARVA)) > 0:
            self.do(self.units(LARVA).random.train(OVERLORD))
            return True
        return False
    
    async def build_ling(self):
        if self.minerals >= 50 and self.supply_left >= 1 and len(self.units(LARVA)) > 0 and len(self.structures(SPAWNINGPOOL).ready) > 0:
            self.do(self.units(LARVA).random.train(ZERGLING))
            print("make ling")
            return True
        return False
    
    async def build_queen(self):
        if self.minerals >= 150 and self.supply_left >= 2:
            if len(self.structures({HATCHERY, LAIR, HIVE}).ready.idle) > 0:
                self.do(self.structures({HATCHERY, LAIR, HIVE}).ready.idle.random.train(QUEEN))
                return True
        return False
    
    async def build_pool(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.builder_drone = self.select_build_worker(self.start_location).tag
            self.remove_drone(self.builder_drone)
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
            builder = self.units.tags_in([self.builder_drone])[0]
            self.build_location = self.start_location + self.start_location - builder.position
            if self.build_location.distance_to(self.structures({HATCHERY, LAIR, HIVE}).ready.random) < 4:
                print("too close")
                self.build_location = self.build_location + self.start_location - builder.position
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self._client.debug_sphere_out(Point3((builder.position[0], builder.position[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.move(self.build_location))
        else:
            builder = self.units.tags_in([self.builder_drone])[0]
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self._client.debug_sphere_out(Point3((builder.position[0], builder.position[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.move(self.build_location))
        
        if self.minerals >= 200:
            if self.builder_drone is None:
                return False
            self.do(builder.build(SPAWNINGPOOL, self.build_location))
            print("build pool")
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            return True
        return False
    
    async def build_hatch(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.builder_drone = self.select_build_worker(self.start_location).tag
            self.remove_drone(self.builder_drone)
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
            builder = self.units.tags_in([self.builder_drone])[0]
            self.build_location = await self.get_next_expansion()
            self.do(builder.move(self.build_location))
        else:
            builder = self.units.tags_in([self.builder_drone])[0]
            self.do(builder.move(self.build_location))
        
        if self.minerals >= 300:
            if self.builder_drone is None:
                return False
            self.do(builder.build(HATCHERY, self.build_location))
            return True
        return False

########################################
############## OVERLORDS ###############
########################################
    
    def position_new_overlord(self, unit):
        for pos in self.overlord_positions:
            if self.convert_location(Point2(pos)) not in self.position_to_ovi_dict:
                self.position_to_ovi_dict[self.convert_location(Point2(pos))] = unit.tag
                self.do(unit.move(self.convert_location(Point2(pos))))
                break
            
    async def position_overlords(self):
        """
        for i in range(0, len(self.overlord_positions)):
            pos = self.convert_location(self.overlord_positions[i])
            height = self.get_terrain_z_height(Point2(self.overlord_positions[i]))
            self._client.debug_sphere_out(Point3((pos[0], pos[1], height)), 2, color = Point3((255, 255, 0)))
            self._client.debug_text_world("ovi " + str(i), Point3((pos[0], pos[1], height)), Point3((255, 255, 0)), 16)
        
        for i in range(0, len(self.rally_points)):
            pos = self.convert_location(self.rally_points[i])
            height = self.get_terrain_z_height(Point2(self.rally_points[i]))
            self._client.debug_sphere_out(Point3((pos[0], pos[1], height)), 2, color = Point3((255, 0, 0)))
            self._client.debug_text_world("rally " + str(i), Point3((pos[0], pos[1], height)), Point3((255, 0, 0)), 16)
        """   
        
        new_expos = self.check_enemy_expansions()
        if new_expos[1]:
            if self.convert_location(Point2(self.overlord_positions[6])) in self.position_to_ovi_dict:
                ovi_tag = self.position_to_ovi_dict[self.convert_location(Point2(self.overlord_positions[6]))]
                if self.units.tags_in([ovi_tag]):
                    self.position_new_overlord(self.units.tags_in([ovi_tag])[0])
        if new_expos[2]:
            if self.convert_location(Point2(self.overlord_positions[7])) in self.position_to_ovi_dict:
                ovi_tag = self.position_to_ovi_dict[self.convert_location(Point2(self.overlord_positions[7]))]
                if self.units.tags_in([ovi_tag]):
                    self.position_new_overlord(self.units.tags_in([ovi_tag])[0])
        if new_expos[3]:
            if self.convert_location(Point2(self.overlord_positions[8])) in self.position_to_ovi_dict:
                ovi_tag1 = self.position_to_ovi_dict[self.convert_location(Point2(self.overlord_positions[8]))]
                if self.units.tags_in([ovi_tag1]):
                    self.position_new_overlord(self.units.tags_in([ovi_tag1])[0])
            if self.convert_location(Point2(self.overlord_positions[12])) in self.position_to_ovi_dict:
                ovi_tag2 = self.position_to_ovi_dict[self.convert_location(Point2(self.overlord_positions[12]))]
                if self.units.tags_in([ovi_tag2]):
                    self.position_new_overlord(self.units.tags_in([ovi_tag2])[0])
        if new_expos[4]:
            if self.convert_location(Point2(self.overlord_positions[9])) in self.position_to_ovi_dict:
                ovi_tag = self.position_to_ovi_dict[self.convert_location(Point2(self.overlord_positions[9]))]
                if self.units.tags_in([ovi_tag]):
                    self.position_new_overlord(self.units.tags_in([ovi_tag])[0])
        if new_expos[5]:
            if self.convert_location(Point2(self.overlord_positions[20])) in self.position_to_ovi_dict:
                ovi_tag = self.position_to_ovi_dict[self.convert_location(Point2(self.overlord_positions[20]))]
                if self.units.tags_in([ovi_tag]):
                    self.position_new_overlord(self.units.tags_in([ovi_tag])[0])
    

                
    

########################################
############### SCOUTING ###############
########################################



    async def scouting(self):
        #send scouts
        if self.scouts_sent == 0 and self.time >= 150:
            if self.enemy_expos[0] == 0:
                #enemy natural is late
                await self.send_early_scout()
            self.scouts_sent += 1
            print("early scout")
        elif self.scouts_sent == 1 and self.time >= 300:
            await self.send_scout()
            self.scouts_sent += 1
            print("first scout")
        elif self.scouts_sent == 2 and self.time >= 480:
            await self.send_scout()
            self.scouts_sent += 1
            print("second scout")
        elif self.scouts_sent == 3 and self.time >= 600:
            await self.send_scout()
            self.scouts_sent += 1
            print("third scout")
        """
        if self.enemy_expos[0] and self.time < 80:
            # enemy went nexus first
            # punsih with lings
            print("seen nexus first")
        elif self.enemy_expos[0] == 0 and self.time > 105:
            # enemy natural is late
            print("seen late natural")
        elif self.enemy_expos[1] + self.enemy_expos[2] > 0 and self.time < 240:
            # emey took 3rd early
            print("seen early 3rd")
        elif self.enemy_expos[1] + self.enemy_expos[2] == 0 and self.time > 300:
            # enemy 3rd is late
            print("seen late 3rd")
        elif self.enemy_expos[1] + self.enemy_expos[2] + self.enemy_expos[3] + self.enemy_expos[4] > 1 and self.time < 480:
            # enemy took 4th early
            print("seen early 4th")
        elif self.enemy_expos[1] + self.enemy_expos[2] + self.enemy_expos[3] + self.enemy_expos[4] == 1 and self.time > 540:
            # enemy 4th is late
            print("seen late 4th")
        """
        #count enemy buildings
        """gates = 0
        robos = 0
        stargates = 0
        forges = 0
        batteries = 0
        cannons = 0
        twilights = 0
        fleet_beacons = 0
        gases = 0
        cores = 0
        archives = 0
        dark_shrines = 0
        robo_bays = 0
        for building in self.enemy_structures():
            if building.type_id == UnitTypeId.GATEWAY or building.type_id == UnitTypeId.WARPGATE:
                gates += 1
            elif building.type_id == UnitTypeId.ROBOTICSFACILITY:
                 robos += 1
            elif building.type_id == UnitTypeId.STARGATE:
                 stargates += 1
            elif building.type_id == UnitTypeId.FORGE:
                 forges += 1
            elif building.type_id == UnitTypeId.SHIELDBATTERY:
                 batteries += 1
            elif building.type_id == UnitTypeId.PHOTONCANNON:
                 cannons += 1
            elif building.type_id == UnitTypeId.TWILIGHTCOUNCIL:
                 twilights += 1
            elif building.type_id == UnitTypeId.FLEETBEACON:
                 fleet_beacons += 1
            elif building.type_id == UnitTypeId.ASSIMILATOR:
                 gases += 1
            elif building.type_id == UnitTypeId.CYBERNETICSCORE:
                 cores += 1
            elif building.type_id == UnitTypeId.TEMPLARARCHIVE:
                 archives += 1
            elif building.type_id == UnitTypeId.DARKSHRINE:
                 dark_shrines += 1
            elif building.type_id == UnitTypeId.ROBOTICSBAY:
                 robo_bays += 1"""
        #respond to scouts
        if self.proxy_location:
            if len(self.enemy_structures) == 0:
                self.proxy_location = None
                self.proxy_status = ProxyStatus.NONE
            else:
                if self.proxy_location.distance_to_closest(self.enemy_structures) > 10:
                    self.proxy_location = None
                    self.proxy_status = ProxyStatus.NONE
        if self.time < 240:
            #proxy
            if self.proxy_status == ProxyStatus.NONE and len(self.enemy_structures) > 0:
                furthest_building = self.enemy_start_locations[0].furthest(self.enemy_structures)
                if self.enemy_start_locations[0].distance_to(furthest_building) > 50:
                    await self.chat_send("Really? A proxy?")
                    self.proxy_location = furthest_building.position
                    self.proxy_status = ProxyStatus.PR_RAX_STARTED
                    await self.enter_pr_rax_started()
                    await self.gauge_proxy_level()
            elif self.proxy_status != ProxyStatus.NONE:
                await self.gauge_proxy_level()
                await self.deny_proxy()
   
    async def update_units_needs(self):
        # special events
        if self.proxy_status != ProxyStatus.NONE:
            self.drone_need = 0
            self.queen_need = round(self.time / 120)
            if self.vespene >= 100 and not self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED):
                self.zergling_need = 0
            else:
                self.zergling_need = 50
            return
        
        #drones
        if len(self.townhalls) < 3 and self.expansion_need == 100:
            self.drone_need = 25
        elif len(self.units(ZERGLING)) + self.already_pending(ZERGLING) + len(self.units(BANELING)) + self.already_pending(BANELING)  < self.zergling_need:
            self.drone_need == 25
        else:
            self.drone_need = min(80, len(self.townhalls) * 16 + len(self.structures(EXTRACTOR)) * 3)
        #queens
        self.queen_need = min(8, len(self.townhalls.ready) * 2 + 2)
        supply = 0
        for tag in self.enemy_unit_tags.keys():
            if self.enemy_unit_tags[tag] not in [PROBE, DRONE, SCV]:
                supply += self.calculate_supply_cost(self.enemy_unit_tags[tag])
        if self.army_composition == ArmyComp.LING_BANE_HYDRA:
            #lings
            if self.supply_workers + self.already_pending(DRONE) < 80:
                if self.structures(BANELINGNEST).ready:
                    if self.structures(HYDRALISKDEN):
                        self.zergling_need == supply * .5
                    else:
                        self.zergling_need = supply
                else:
                    self.zergling_need = min(supply * 2, 20)
            else:
                self.zergling_need = 150 - ((self.queen_need + self.infestor_need) * 2)
            #banes
            self.baneling_need = len(self.units(ZERGLING)) / 2
            #hydras
            if len(self.structures(HYDRALISKDEN)) > 0:
                if self.supply_workers + self.already_pending(DRONE) < 80:
                    self.hydralisk_need = supply * 0.25
                else:
                    self.hydralisk_need = 20 - ((self.queen_need + self.infestor_need) / 2)
        elif self.army_composition == ArmyComp.ROACH_HYDRA:
            #roaches
            if len(self.structures(ROACHWARREN)) > 0:
                self.zergling_need = 0
                if self.supply_workers + self.already_pending(DRONE) < 80:
                    if len(self.structures(HYDRALISKDEN)) > 0:
                        self.roach_need = supply * 0.25
                    else:
                        self.roach_need = min(30, supply * 0.5)
                else:
                    self.roach_need = 30
            elif supply > 10:
                self.zergling_need = supply * .5
            #hydras
            if len(self.structures(HYDRALISKDEN)) > 0:
                if self.supply_workers + self.already_pending(DRONE) < 80:
                    self.hydralisk_need = supply * 0.25
                else:
                    self.hydralisk_need = 30
        elif self.army_composition == ArmyComp.ROACH_SWARM_HOST:
            #roaches
            if len(self.structures(ROACHWARREN)) > 0:
                self.zergling_need = 0
                if self.supply_workers + self.already_pending(DRONE) < 80:
                    if len(self.structures(HYDRALISKDEN)) > 0:
                        self.roach_need = supply * 0.25
                    else:
                        self.roach_need = min(30, supply * 0.5)
                else:
                    self.roach_need = 30
            elif supply > 10:
                self.zergling_need = supply * .5
            #swarm hosts
            if len(self.structures(INFESTATIONPIT)) > 0 and (len(self.structures(NYDUSNETWORK)) > 0 or self.already_pending(NYDUSNETWORK)):
                if self.supply_workers + self.already_pending(DRONE) < 60:
                    self.swarmhost_need = 10
                else:
                    self.swarmhost_need = 14
        if self.army_composition == ArmyComp.LING_BANE_MUTA:
            #lings
            if self.supply_workers + self.already_pending(DRONE) < 80:
                if self.structures(BANELINGNEST).ready:
                    if self.structures({SPIRE, GREATERSPIRE}):
                        self.zergling_need == supply * .5
                    else:
                        self.zergling_need = supply
                else:
                    self.zergling_need = min(supply * 2, 20)
            else:
                self.zergling_need = 70
            #banes
            self.baneling_need = len(self.units(ZERGLING)) / 2
            #mutas
            if len(self.structures({SPIRE, GREATERSPIRE})) > 0:
                if self.supply_workers + self.already_pending(DRONE) < 80:
                    self.mutalisk_need = 10
                else:
                    self.mutalisk_need = 25
    
    async def update_building_need(self):
        # special events
        if self.proxy_status != ProxyStatus.NONE:
            self.expansion_need = 0
            return
        
        # the enemy has the same number of bases as us
        if sum(self.enemy_expos) + 1 >= len(self.townhalls) + self.already_pending(HATCHERY) or self.time >= self.last_expansion_time + 120:
            self.expansion_need = 100
        else:
            self.expansion_need = 0

    async def update_enemy_units(self):
        for unit in self.enemy_units:
            if unit.tag not in self.enemy_unit_tags.keys():
                self.enemy_unit_tags[unit.tag] = unit.type_id
                #print("+1 " + str(unit.type_id))
                if unit.type_id in self.enemy_unit_numbers.keys():
                    self.enemy_unit_numbers[unit.type_id] = self.enemy_unit_numbers[unit.type_id] + 1
                else:
                    self.enemy_unit_numbers[unit.type_id] = 1

    async def show_scouted_info(self):
        print(str(self.enemy_structures))
                
    async def send_scout(self):
        if self.convert_location(Point2(self.overlord_positions[2])) in self.position_to_ovi_dict:
            ovi_tag = self.position_to_ovi_dict[self.convert_location(Point2(self.overlord_positions[2]))]
            print("scout " + str(ovi_tag))
            if len(self.units.tags_in([ovi_tag])) == 0:
                return False
            for pos in self.main_scout_path:
                self.do(self.units.tags_in([ovi_tag])[0].move(self.convert_location(Point2(pos)), True)) # TODO fix index out of range error
            self.position_to_ovi_dict.pop(self.convert_location(Point2(self.overlord_positions[2])))
            return True
        return False
    
    async def send_early_scout(self):
        if self.convert_location(Point2(self.overlord_positions[0])) in self.position_to_ovi_dict:
            ovi_tag = self.position_to_ovi_dict[self.convert_location(Point2(self.overlord_positions[0]))]
            for i in [1, 0, 3, 2]:
                self.do(self.units.tags_in([ovi_tag])[0].move(self.convert_location(Point2(self.main_scout_path[i])), True))
    
    async def send_ling_scouts(self):
        for i in range(0, len(self.zergling_scout_tags)):
            if len(self.units.tags_in([self.zergling_scout_tags[i]])) == 0:
                return False
        for i in range(0, len(self.zergling_scout_tags)):
            ling = self.units.tags_in([self.zergling_scout_tags[i]])[0]
            for j in range(0, len(self.scouting_path[i])):
                self.do(ling.move(self.convert_location(Point2(self.scouting_path[i][j])), True))
        return True
    
    async def scout_with_lings(self):
        if not (self.enemy_expos[1] or self.enemy_expos[2]):
            for i in range(0, len(self.zergling_scout_tags)):
                if not self.zergling_scout_tags[i]:
                    continue
                ling = self.units.tags_in([self.zergling_scout_tags[i]])[0]
                if ling.is_idle:
                    self.do(ling.move(self.convert_location(Point2(self.scouting_path[i][-1])), True))
        if not self.enemy_expos[0] and self.time - self.last_ling_scout_time > 30:
            if len(self.units.tags_in(self.zergling_scout_tags)) > 0:
                ling = self.units.tags_in(self.zergling_scout_tags).random
                if ling.is_idle:
                    self.do(ling.move(self.convert_location(self.expos[7])))
                    self.last_ling_scout_time = self.time
                
            
            
    
    def check_enemy_expansions(self):
        new_expos = [0, 0, 0, 0, 0, 0]
        expo_numbers = [7, 3, 9, 6, 2, 4]
        if len(self.enemy_structures({NEXUS, HATCHERY, LAIR, HIVE, COMMANDCENTER, ORBITALCOMMAND, PLANETARYFORTRESS})) > 0:
            for i in range(0, 5):
                if self.convert_location(Point2(self.expos[expo_numbers[i]])).distance_to_closest(self.enemy_structures({NEXUS, HATCHERY, LAIR, HIVE, COMMANDCENTER, ORBITALCOMMAND, PLANETARYFORTRESS})) < 3:
                    if not self.enemy_expos[i]:
                        new_expos[i] = 1
                        self.enemy_expos[i] = 1
                else:
                    self.enemy_expos[i] = 0
        return new_expos
    
    async def track_enemy_army_position(self):
        if len(self.enemy_units.exclude_type({SCV, DRONE, PROBE})) < 0:
            return
        lone_enemy_units = Units([], self)
        grouped_enemy_units = self.enemy_units.exclude_type({SCV, DRONE, PROBE})
        
        i = 1
        n = len(grouped_enemy_units)
        while i < n:
            unit = grouped_enemy_units[i]
            if len(grouped_enemy_units.closer_than(3, unit)) > 1:
                # if there are units closer than 3 then move on
                i += 1
            else:
                # if not then remove it from the list and add it to the loners list
                lone_enemy_units.append(unit)
                grouped_enemy_units.remove(unit)
                n -= 1
        
        for unit in lone_enemy_units:
            self._client.debug_sphere_out(unit.position3d, 1, color = Point3((255, 0, 0)))
        
        if len(grouped_enemy_units) > 0:
            enemy_unit_groups = []
            group_num = 0
            while len(grouped_enemy_units) > 0:
                # grab the first unit and add it to a new group
                unit = grouped_enemy_units[0]
                grouped_enemy_units.remove(unit)
                enemy_unit_groups.append(Units([unit], self))
                i = 0
                n = len(enemy_unit_groups[group_num])
                while i < n:
                    # test each unit in a group and add units close to it to the group
                    test_unit = enemy_unit_groups[group_num][i]
                    close_units = grouped_enemy_units.closer_than(5, test_unit)
                    if len(close_units) > 0:
                        for close_unit in close_units:
                            # when a unit is added to a group remove it from the origional list
                            enemy_unit_groups[group_num].append(close_unit)
                            grouped_enemy_units.remove(close_unit)
                            n += 1
                    i += 1
                group_num += 1
            
            expo_numbers = [7, 3, 9, 6, 2, 4]
            # display green sphere over top each group
            for group in enemy_unit_groups:
                pos = group.center
                height = self.get_terrain_z_height(pos)
                self._client.debug_sphere_out(Point3((pos[0], pos[1], height)), 4, color = Point3((0, 255, 0)))
                enemy_bases_locations = []
                
            group = max(enemy_unit_groups, key = lambda k: len(k))
            pos = group.center
            for i in range(0, len(self.enemy_expos)):
                if self.enemy_expos[i] > 0:
                    enemy_bases_locations.append(self.convert_location(self.expos[expo_numbers[i]]))
            closest_position = pos.closest(self.army_positions + enemy_bases_locations)
            if closest_position in enemy_bases_locations:
                #enemy is on the defensive
                self.enemy_army_state = EnemyArmyState.DEFENDING
                self.enemy_attack_point = None
            else:
                if closest_position in [self.army_positions[i] for i in [5, 6, 10, 14, 17]]:
                    self.enemy_army_state = EnemyArmyState.PREPARING_ATTACK
                else:
                    self.enemy_army_state = EnemyArmyState.MOVING_TO_ATTACK
                dijkstras_graph = DijkstraSPF(self.map_graph, self.army_positions.index(closest_position))
                #print("%-5s %-5s" % ("label", "distance"))
                #for u in [0, 2, 8, 9, 23]:
                    #print(str(u) + "    " + str(dijkstras_graph.get_distance(u)))
                closest_point = min([0, 2, 8, 9, 23], key = lambda k: dijkstras_graph.get_distance(k))
                #print("ea pos: " + str(self.army_positions.index(closest_position)))
                #print("closest point: " + str(closest_point))
                most_likely_path = dijkstras_graph.get_path(closest_point)
                for i in range(0, len(most_likely_path) - 1):
                    h1 = self.get_terrain_z_height(Point2(self.army_positions[most_likely_path[i]])) + .1
                    h2 = self.get_terrain_z_height(Point2(self.army_positions[most_likely_path[i + 1]])) + .1
                    pos1 = Point3((self.army_positions[most_likely_path[i]][0], self.army_positions[most_likely_path[i]][1], h1))
                    pos2 = Point3((self.army_positions[most_likely_path[i + 1]][0], self.army_positions[most_likely_path[i + 1]][1], h2))
                    self._client.debug_sphere_out(pos1, 4, color = Point3((255, 0, 255)))
                    self._client.debug_sphere_out(pos2, 4, color = Point3((255, 0, 255)))
                    self._client.debug_line_out(pos1, pos2, color = Point3((255, 0, 255)))
                self.enemy_attack_point = Point2(self.army_positions[most_likely_path[len(most_likely_path) - 1]]).closest(self.townhalls)
                
        # 0, 2, 7, 8, 9, 23
        """
        attacking_units = self.enemy_units.subgroup(unit for unit in self.enemy_units if self.has_creep(unit.position))
        lone_enemy_units = []
        if len(attacking_units) < 2:
            for unit in attacking_units:
                lone_enemy_units.append(unit)
        else:
            for unit in attacking_units:
                if unit.position.distance_to(unit.position.sort_by_distance(attacking_units)[1]) > 5:
                    lone_enemy_units.append(unit)
        attacking_units = attacking_units.subgroup(unit for unit in attacking_units if unit not in lone_enemy_units)
        
        if len(attacking_units) >= 2:
            self.enemy_army_position = attacking_units.center
            height = self.get_terrain_z_height(self.enemy_army_position)
            self._client.debug_sphere_out(Point3((self.enemy_army_position[0], self.enemy_army_position[1], height)), 4, color = Point3((255, 0, 0)))
        else:
            self.enemy_army_position == None
            
        for unit in lone_enemy_units:
            self._client.debug_sphere_out(unit.position3d, 1, color = Point3((0, 0, 255)))
        """
    
    async def update_proxy_progress(self):
        # update enemy units in proxy
        proxy_units = None
        if len(self.enemy_units) > 0:
            proxy_units = self.enemy_units.further_than(50, self.enemy_start_locations[0])
            for unit in proxy_units:
                new_unit = True
                for unit_info in self.proxy_units:
                    if unit.tag == unit_info[0]:
                        unit_info = (unit_info[0], unit_info[1], unit.health)
                        new_unit = False
                        break
                if new_unit:
                    print("seen new proxy unit: " + str(unit.type_id))
                    self.proxy_units.append((unit.tag, unit.type_id, unit.health))
        
        # update enemy bulidings in proxy
        proxy_buildings = None
        if len(self.enemy_structures) > 0:
            proxy_buildings = self.enemy_structures.further_than(50, self.enemy_start_locations[0])
            for building in proxy_buildings:
                if building.is_snapshot:
                    continue
                new_building = True
                for building_info in self.proxy_buildings:
                    if building.tag == building_info[0]:
                        new_building = False
                        break
                if new_building:
                    print("seen new proxy structure: " + str(building.type_id))
                    if building.type_id == BARRACKS:
                        self.proxy_buildings.append((building.tag, building.type_id, building.build_progress - (5 / 644)))
                    elif building.type_id == BUNKER:
                        self.proxy_buildings.append((building.tag, building.type_id, building.build_progress - (5 / 406)))
                        
        if len([unit for unit in self.proxy_units if unit[1] == SCV]) > 0:
            # update build percent for enemy buildings only if there are still scvs alive
            for i in range(0, len(self.proxy_buildings)):
                if self.proxy_buildings[i][1] == BARRACKS:
                    self.proxy_buildings[i] = (self.proxy_buildings[i][0], self.proxy_buildings[i][1], min(1, self.proxy_buildings[i][2] + (5 / 644)))
                elif self.proxy_buildings[i][1] == BUNKER:
                    self.proxy_buildings[i] = (self.proxy_buildings[i][0], self.proxy_buildings[i][1], min(1, self.proxy_buildings[i][2] + (5 / 406)))
        
    
    async def gauge_proxy_level(self):
        await self.update_proxy_progress()
        if len(self.proxy_buildings) == 0 and len(self.proxy_units) == 0:
            self.proxy_status = ProxyStatus.NONE
            await self.chat_send("proxy ended")
        
        if self.enemy_race == Race.Random:
            return

        if self.enemy_race == Race.Terran:
            if self.proxy_status == ProxyStatus.PR_RAX_STARTED:
                # query build status for barrack
                rax = [building for building in self.proxy_buildings if building[1] == BARRACKS]
                if rax and any([building[2] >= 1 for building in rax]):
                    await self.chat_send("some rax finished")
                    await self.enter_pr_some_rax_finished()
                    self.proxy_status = ProxyStatus.PR_SOME_RAX_FINISHED
                # query build progress for bunkers
                bunkers = [building for building in self.proxy_buildings if building[1] == BUNKER]
                if bunkers:
                    if not any([unit[1] == MARINE for unit in self.proxy_units]):
                        await self.chat_send("unprotected bunker started")
                        await self.enter_pr_unprotected_bunker()
                        self.proxy_status = ProxyStatus.PR_UNPROTECTED_BUNKER
                    else:
                        print("protected bunker started")
                        self.proxy_status = ProxyStatus.PR_PROTECTED_BUNKER
                # attack without bunkers?
                marines = [unit for unit in self.enemy_units if unit.type_id == MARINE]
                if marines and any([unit.position.distance_to_closest(self.townhalls) < 10 for unit in marines]):
                    print("attacking without bunker")
                    self.proxy_status = ProxyStatus.PR_NO_BUNKER_ATTACK
            elif self.proxy_status == ProxyStatus.PR_SOME_RAX_FINISHED:
                if not self.breaking_proxy:
                    # query build status for barrack
                    rax = [building for building in self.proxy_buildings if building[1] == BARRACKS]
                    if rax and not any([building[2] < 1 for building in rax]):
                        await self.chat_send("all rax finished")
                        await self.enter_pr_all_rax_finished()
                        self.proxy_status = ProxyStatus.PR_ALL_RAX_FINISHED
                # query build progress for bunkers
                bunkers = [building for building in self.proxy_buildings if building[1] == BUNKER]
                if bunkers:
                    if not any([unit[1] == MARINE for unit in self.proxy_units]):
                        print("unprotected bunker started")
                        await self.enter_pr_unprotected_bunker()
                        self.proxy_status = ProxyStatus.PR_UNPROTECTED_BUNKER
                    else:
                        print("protected bunker started")
                        self.proxy_status = ProxyStatus.PR_PROTECTED_BUNKER
                # attack without bunkers?
                marines = [unit for unit in self.enemy_units if unit.type_id == MARINE]
                if marines and any([unit.position.distance_to_closest(self.townhalls) < 10 for unit in marines]):
                    print("attacking without bunker")
                    self.proxy_status = ProxyStatus.PR_NO_BUNKER_ATTACK
            elif self.proxy_status == ProxyStatus.PR_ALL_RAX_FINISHED:
                # query build status for barrack
                rax = [building for building in self.proxy_buildings if building[1] == BARRACKS]
                if rax and any([building[2] < 1 for building in rax]):
                    await self.chat_send("some rax finished")
                    await self.enter_pr_some_rax_finished()
                    self.proxy_status = ProxyStatus.PR_SOME_RAX_FINISHED
                # query build progress for bunkers
                bunkers = [building for building in self.proxy_buildings if building[1] == BUNKER]
                if bunkers:
                    if not any([unit[1] == MARINE for unit in self.proxy_units]):
                        print("unprotected bunker started")
                        await self.enter_pr_unprotected_bunker()
                        self.proxy_status = ProxyStatus.PR_UNPROTECTED_BUNKER
                    else:
                        print("protected bunker started")
                        self.proxy_status = ProxyStatus.PR_PROTECTED_BUNKER
                # attack without bunkers?
                marines = [unit for unit in self.enemy_units if unit.type_id == MARINE]
                if marines and any([unit.position.distance_to_closest(self.townhalls) < 10 for unit in marines]):
                    print("attacking without bunker")
                    self.proxy_status = ProxyStatus.PR_NO_BUNKER_ATTACK
            elif self.proxy_status == ProxyStatus.PR_UNPROTECTED_BUNKER:
                # query build progress for bunkers
                if any([unit[1] == MARINE for unit in self.proxy_units]):
                    self.proxy_status = ProxyStatus.PR_PROTECTED_BUNKER
                elif any([building[1] == BUNKER and building[2] >= 1 for building in self.proxy_buildings]):
                    print("bunker finished")
                    self.proxy_status = ProxyStatus.PR_BUNKER_FINISHED
            elif self.proxy_status == ProxyStatus.PR_PROTECTED_BUNKER:
                # query build progress for bunkers
                if any([building[1] == BUNKER and building[2] >= 1 for building in self.proxy_buildings]):
                    print("bunker finished")
                    self.proxy_status = ProxyStatus.PR_BUNKER_FINISHED
            elif self.proxy_status == ProxyStatus.PR_NO_BUNKER_ATTACK:
                # query build progress for bunkers
                bunkers = [building for building in self.proxy_buildings if building[1] == BUNKER]
                if bunkers:
                    if not any([unit[1] == MARINE for unit in self.proxy_units]):
                        print("unprotected bunker started")
                        await self.enter_pr_unprotected_bunker()
                        self.proxy_status = ProxyStatus.PR_UNPROTECTED_BUNKER
                    else:
                        print("protected bunker started")
                        self.proxy_status = ProxyStatus.PR_PROTECTED_BUNKER
            elif self.proxy_status == ProxyStatus.PR_BUNKER_FINISHED:
                return
                
    
########################################
################# CREEP ################
########################################

    async def spread_creep(self):
        for tumor in self.structures(CREEPTUMORBURROWED):
            if AbilityId.BUILD_CREEPTUMOR_TUMOR in await self.get_available_abilities(tumor):
                for spot in self.creep_spread_to:
                    if tumor.distance_to_squared(spot) < 100:
                        self.do(tumor(AbilityId.BUILD_CREEPTUMOR_TUMOR, spot))
                        self.inactive_creep_tumors.append(tumor)
                        self.creep_spread_to.remove(spot)
                        break
        
        if self.creep_queen_state == QueenState.SPREAD_CREEP:
            await self.place_creep_tumors()
            if self.creep_coverage >= .4 or self.enemy_army_state == EnemyArmyState.PREPARING_ATTACK:
                self.creep_queen_state = QueenState.SPREAD_CAREFULLY
                print("creep reached 40%, start saving energy")
            elif self.creep_coverage >= .6 or self.enemy_army_state == EnemyArmyState.MOVING_TO_ATTACK:
                print("creep reached 60%, stop placing tumors")
                self.creep_queen_state = QueenState.DEFEND
        elif self.creep_queen_state == QueenState.SPREAD_CAREFULLY:
            await self.place_creep_tumors_carefully()
            if self.creep_coverage < .4 and self.enemy_army_state == EnemyArmyState.DEFENDING:
                print("creep receeded to <40%, stop saving energy")
                self.creep_queen_state = QueenState.SPREAD_CREEP
            elif self.creep_coverage >= .6 or self.enemy_army_state == EnemyArmyState.MOVING_TO_ATTACK:
                print("creep reached 60%, stop placing tumors")
                self.creep_queen_state = QueenState.DEFEND
        elif self.creep_queen_state == QueenState.DEFEND:
            if self.creep_coverage < .6 and not self.enemy_army_state == EnemyArmyState.MOVING_TO_ATTACK:
                print("creep receeded to <60%, start placing tumors again")
                self.creep_queen_state = QueenState.SPREAD_CAREFULLY
        
            
    
    async def place_creep_tumors(self):
        for queen in self.creep_queens:
            if self.units.tags_in([queen])[0].energy >= 25 and self.units.tags_in([queen])[0].is_idle and len(self.creep_spread_to) > 0 :
                self.do(self.units.tags_in([queen])[0](AbilityId.BUILD_CREEPTUMOR_QUEEN, Point2(self.creep_spread_to.pop(0))))
                
    async def place_creep_tumors_carefully(self):
        for queen in self.creep_queens:
            if self.units.tags_in([queen])[0].energy >= 75 and self.units.tags_in([queen])[0].is_idle and len(self.creep_spread_to) > 0 :
                self.do(self.units.tags_in([queen])[0](AbilityId.BUILD_CREEPTUMOR_QUEEN, Point2(self.creep_spread_to.pop(0))))
                
    async def find_creep_spots(self):
        await self.update_creep_coverage()
        
        locations = []
        current_tumors = self.structures(CREEPTUMOR) + self.structures(CREEPTUMORBURROWED)
        pixel_map = self.game_info.placement_grid
        for  i in range(0, pixel_map.width):
            for j in range(0, pixel_map.height):
                if pixel_map.__getitem__((i, j)) and self.has_creep(Point2((i, j))):
                    # ignore any location inside the main
                    if self.start_location.distance_to(Point2((i, j))) < 30:
                        continue
                    # ignore any point that would block an expo
                    if Point2((i, j)).distance_to_closest(self.expansion_locations_list) < 4:
                        continue
                    # ignore points close to enemies
                    if len(self.enemy_units.exclude_type({DRONE, SCV, PROBE})) and Point2((i, j)).distance_to_closest(self.enemy_units.exclude_type({DRONE, SCV, PROBE})) < 10:
                        continue
                    # find edges of creep
                    edge = False
                    for k in range(i-1, i+2):
                        for l in range(j-1, j+2):
                            if pixel_map.__getitem__((k, l)) and not self.has_creep(Point2((k, l))):
                                edge = True
                    if edge:
                        height = self.get_terrain_z_height(Point2((i, j)))
                        self._client.debug_sphere_out(Point3((i, j, height)), .5, color = Point3((255, 0, 255)))
                        locations.append(Point2((i, j)))
        # sort the locations based on their distance from the natural and their distance to the closest active tumor
        if len(self.structures({CREEPTUMOR, CREEPTUMORQUEEN})) > 0:
            locations = sorted(locations, key=lambda point: point.distance_to(self.convert_location(Point2(self.expos[10]))) - 5 * point.distance_to_closest(self.structures({CREEPTUMOR, CREEPTUMORQUEEN})))         
        else:
            locations = sorted(locations, key=lambda point: point.distance_to(self.convert_location(Point2(self.expos[10]))))
        # add all predetermined creep locations to the front
        for pos in self.creep_locations:
            if (len(self.structures(CREEPTUMOR)) == 0 or self.convert_location(Point2(pos)).distance_to_closest(current_tumors) > 2) and self.has_creep(self.convert_location(Point2(pos))):
                locations.insert(0, self.convert_location(Point2(pos)))
        return locations
    
    async def update_creep(self):
        if not self.updated_creep and int(self.time) % 2 == 0:
            self.updated_creep = True
            self.creep_spread_to = await self.find_creep_spots()
        elif self.updated_creep and int(self.time) % 2 == 1:
            self.updated_creep = False
    
    async def update_creep_coverage(self):
        pixel_map = self.game_info.placement_grid
        valid_points = 0
        points_with_creep = 0
        for  i in range(0, pixel_map.width):
            for j in range(0, pixel_map.height):
                if pixel_map.__getitem__((i, j)):
                    valid_points += 1
                    if self.has_creep(Point2((i, j))):
                        points_with_creep += 1
        self.creep_coverage = points_with_creep / valid_points
   
    def get_best_tumor_location(self, unit):
        assert isinstance(unit, Unit)
        possible_locations = []
        for x in range(int(unit.position[0] - 10), int(unit.position[0] + 10), 2):
            for y in range(int(unit.position[1] - 10), int(unit.position[1] + 10), 2):
                loc = Point2((x, y))
                # ignore any point not in the tumors range
                if unit.position.distance_to(loc) >= 10:
                    continue
                # ignore any point that would block an expo
                if loc.distance_to_closest(self.expansion_locations_list) < 4:
                    continue
                if self.has_creep(loc) and self.in_placement_grid(loc) and self.is_visible(loc):
                    possible_locations.append(loc)
        best_so_far = Point2((0, 0))
        # find the point farthest from any inactive tumors
        if len(possible_locations) > 0:
            if len(self.inactive_creep_tumors) == 0:
                best_so_far = self.enemy_start_locations[0].closest(possible_locations)
            else:
                best_dist = 0
                for loc in possible_locations:
                    dist = loc.distance_to_closest(self.inactive_creep_tumors)
                    if dist > best_dist:
                        best_dist = dist
                        best_so_far = loc
        return best_so_far

    def spread_inject_queens(self):
        used_queens = []
        for hatch in self.townhalls.ready:
            closest_queens = self.units.tags_in(self.injecting_queens)._list_sorted_by_distance_to(hatch)
            for queen in closest_queens:
                if queen not in used_queens:
                    #print("hatch: " + str(hatch) + " queen: " + str(queen))
                    self.do(queen.move(hatch))
                    used_queens.append(queen)
                    break

########################################
################# NYDUS ################
########################################

    async def find_nydus_spot(self):
        possible_locations = []
        if self.enemy_expos[5]:
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[11])) and self.is_visible(self.convert_location(self.nydus_positions[11])):
                possible_locations.append(self.convert_location(self.nydus_positions[11]))
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[9])) and self.is_visible(self.convert_location(self.nydus_positions[9])):
                possible_locations.append(self.convert_location(self.nydus_positions[9]))
        if self.enemy_expos[4]:
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[4])) and self.is_visible(self.convert_location(self.nydus_positions[4])):
                possible_locations.append(self.convert_location(self.nydus_positions[4]))
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[2])) and self.is_visible(self.convert_location(self.nydus_positions[2])):
                possible_locations.append(self.convert_location(self.nydus_positions[2]))
        if self.enemy_expos[3]:
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[5])) and self.is_visible(self.convert_location(self.nydus_positions[5])):
                possible_locations.append(self.convert_location(self.nydus_positions[5]))
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[9])) and self.is_visible(self.convert_location(self.nydus_positions[9])):
                possible_locations.append(self.convert_location(self.nydus_positions[9]))
        if self.enemy_expos[2]:
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[1])) and self.is_visible(self.convert_location(self.nydus_positions[1])):
                possible_locations.append(self.convert_location(self.nydus_positions[1]))
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[2])) and self.is_visible(self.convert_location(self.nydus_positions[2])):
                possible_locations.append(self.convert_location(self.nydus_positions[2]))
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[6])) and self.is_visible(self.convert_location(self.nydus_positions[6])):
                possible_locations.append(self.convert_location(self.nydus_positions[6]))
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[10])) and self.is_visible(self.convert_location(self.nydus_positions[10])):
                possible_locations.append(self.convert_location(self.nydus_positions[10]))
        if self.enemy_expos[1]:
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[3])) and self.is_visible(self.convert_location(self.nydus_positions[3])):
                possible_locations.append(self.convert_location(self.nydus_positions[3]))
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[5])) and self.is_visible(self.convert_location(self.nydus_positions[5])):
                possible_locations.append(self.convert_location(self.nydus_positions[5]))
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[11])) and self.is_visible(self.convert_location(self.nydus_positions[11])):
                possible_locations.append(self.convert_location(self.nydus_positions[11]))
        if self.enemy_expos[0]:
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[0])) and self.is_visible(self.convert_location(self.nydus_positions[0])):
                possible_locations.append(self.convert_location(self.nydus_positions[0]))
        if not self.enemy_expos[2] and not self.enemy_expos[4]:
            if self.can_place_single(NYDUSCANAL, self.convert_location(self.nydus_positions[1])) and self.is_visible(self.convert_location(self.nydus_positions[1])):
                possible_locations.append(self.convert_location(self.nydus_positions[1]))
        return possible_locations
    
    async def spawn_nydus_worm(self):
        possible_spots = await self.find_nydus_spot()
        current_nydus_worms = self.structures(NYDUSCANAL)
        if len(current_nydus_worms) == 0:
            for nydus in self.structures(NYDUSNETWORK).ready:
                if AbilityId.BUILD_NYDUSWORM in await self.get_available_abilities(nydus):
                    if len(possible_spots) > 0:
                        spot = random.choice(possible_spots)
                        print("first nydus at " + str(spot))
                        self.do(nydus(AbilityId.BUILD_NYDUSWORM, spot))
        else:
            for nydus in self.structures(NYDUSNETWORK).ready:
                if AbilityId.BUILD_NYDUSWORM in await self.get_available_abilities(nydus):
                    if len(possible_spots) > 0:
                        spot = sorted(possible_spots, key = lambda u: u.position.distance_to_closest(current_nydus_worms))[len(possible_spots) - 1]
                        possible_spots.remove(spot)
                        print("new nydus at " + str(spot))
                        self.do(nydus(AbilityId.BUILD_NYDUSWORM, spot))
                    


########################################
################# MICRO ################
########################################

    async def micro(self):
        need_to_protect = None
        # are we being attacked right now?
        for enemy in self.enemy_units.exclude_type([DRONE, PROBE, SCV]):
            for hatch in self.townhalls:
                if enemy.distance_to(hatch) < 20:
                    need_to_protect = enemy.position
        if self.creep_queen_state == QueenState.DEFEND:
            await self.micro_queen_defense(need_to_protect)
        if self.army_composition == ArmyComp.LING_BANE_HYDRA or self.army_composition == ArmyComp.LING_BANE_MUTA:
            await self.micro_banes()
        if self.army_composition == ArmyComp.LING_BANE_MUTA:
            await self.micro_mutas()
        if self.army_composition == ArmyComp.ROACH_SWARM_HOST:
            await self.spawn_nydus_worm()
            await self.micro_swarm_hosts()
            await self.micro_locusts()
        if len(self.units(INFESTOR)) > 0:
            await self.micro_infestors()
            
        if self.army_state == ArmyState.CONSOLIDATING:
            if need_to_protect:
                self.army_state = ArmyState.PROTECTING
                for unit in self.units.exclude_type([LARVA, EGG, DRONE, QUEEN, OVERLORD, MUTALISK, SWARMHOSTMP]):
                    self.do(unit.attack(need_to_protect))
            # move all units to the consolidation point
            for unit in self.units.exclude_type([LARVA, DRONE, QUEEN, OVERLORD, SWARMHOSTMP]).tags_not_in(self.zergling_scout_tags + self.muta_group_tags):
                if unit.distance_to(Point2(self.convert_location(self.army_spot))) > 10 and unit.is_idle:
                    self.do(unit.move(Point2(self.convert_location(self.army_spot))))
            # if we have more than 90 army supply ready then go to the rally point
            if sum(self.calculate_supply_cost(unit.type_id) for unit in self.units.exclude_type([LARVA, EGG, DRONE, QUEEN, OVERLORD, MUTALISK, SWARMHOSTMP]).tags_not_in(self.zergling_scout_tags)) >= 100:
                self.army_state = ArmyState.RALLYING
                await self.find_attack_and_rally_points()
                print("rally to " + str(self.rally_point))
                self.army_unit_tags = []
                for unit in self.units.exclude_type([LARVA, EGG, DRONE, QUEEN, OVERLORD, MUTALISK, SWARMHOSTMP]).tags_not_in(self.zergling_scout_tags):
                    self.army_unit_tags.append(unit.tag)
                    self.do(unit.attack(Point2(self.rally_point)))
        elif self.army_state == ArmyState.RALLYING:
            # if we're attacked while we're launching an attack then go back to defend
            # TODO determine if we need to defend and how much with
            if need_to_protect:
                self.army_state = ArmyState.PROTECTING
                for unit in self.units.exclude_type([LARVA, EGG, DRONE, QUEEN, OVERLORD, MUTALISK, SWARMHOSTMP]).tags_not_in(self.zergling_scout_tags):
                    self.do(unit.attack(need_to_protect))
            # is everyone in position?
            for unit in self.units.tags_in(self.army_unit_tags):
                if unit.distance_to(Point2(self.rally_point)) > 10:
                    # unit is not yet at the rally point
                    print("waiting on " + str(unit.type_id))
                    self._client.debug_sphere_out(Point3((unit.position3d[0], unit.position3d[1], unit.position3d[2])), 1, color = Point3((0, 255, 0)))
                    return
            # everyone is at the rally point then attack and queue attacking the main
            self.army_state = ArmyState.ATTACKING
            print("attack " + str(self.attack_position))
            for unit in self.units.tags_in(self.army_unit_tags):
                self.do(unit.attack(Point2(self.attack_position)))
                self.do(unit.attack(Point2(self.enemy_start_locations[0]), queue = True))
        elif self.army_state == ArmyState.ATTACKING:
            enemy_supply = 0
            # determine enemy army supply
            for tag in self.enemy_unit_tags.keys():
                if self.enemy_unit_tags[tag] not in [PROBE, DRONE, SCV]:
                    enemy_supply += self.calculate_supply_cost(self.enemy_unit_tags[tag])
            # if we have 2x more army supply then flood new units
            if self.supply_army > enemy_supply * 2:
                for unit in self.units.exclude_type([LARVA, DRONE, QUEEN, OVERLORD, MUTALISK, SWARMHOSTMP]).tags_not_in(self.army_unit_tags + self.zergling_scout_tags):
                    self.army_unit_tags.append(unit.tag)
                    self.do(unit.attack(Point2(self.attack_position)))
                    self.do(unit.attack(Point2(self.enemy_start_locations[0]), queue = True))
            # if the attack has been killed off go back to consolidating
            if len(self.units.tags_in(self.army_unit_tags)) == 0:
                print("consolidate")
                self.army_state = ArmyState.CONSOLIDATING
            for roach in self.units({ROACH, ROACHBURROWED}).tags_in(self.army_unit_tags):
                await self.micro_roach(roach)
            for unit in self.units.tags_in(self.army_unit_tags).idle:
                self.do(unit.attack(Point2(self.attack_position)))
                self.do(unit.attack(Point2(self.enemy_start_locations[0]), queue = True))
        elif self.army_state == ArmyState.PROTECTING:
            # if the attack has been dealt with go back to consolidating
            if need_to_protect == None:
                self.army_state = ArmyState.CONSOLIDATING

    
                    
    async def find_attack_and_rally_points(self):
        if self.enemy_expos[5] == 1:
            print("attack middle base")
            self.rally_point = self.convert_location(self.rally_points[7])
            self.attack_position = self.convert_location(self.expos[4])
        elif self.enemy_expos[4] == 1:
            print("attack triangle 5th")
            self.rally_point = self.convert_location(self.rally_points[0])
            self.attack_position = self.convert_location(self.expos[2])
        elif self.enemy_expos[3] == 1:
            print("attack inline 5th")
            self.rally_point = self.convert_location(self.rally_points[7])
            self.attack_position = self.convert_location(self.expos[6])
        elif self.enemy_expos[2] == 1:
            print("attack triangle 3rd")
            self.rally_point = self.convert_location(self.rally_points[6])
            self.attack_position = self.convert_location(self.expos[9])
        elif self.enemy_expos[1] == 1:
            print("attack inline 3rd")
            self.rally_point = self.convert_location(self.rally_points[5])
            self.attack_position = self.convert_location(self.expos[3])
        elif self.enemy_expos[0] == 1:
            print("attack natural")
            self.rally_point = self.convert_location(self.rally_points[2])
            self.attack_position = self.convert_location(self.expos[7])
        else:
            print("attack anything")
            self.rally_point = self.convert_location(self.rally_points[7])
            self.attack_position = self.enemy_structures.random.position
            
    async def micro_queen_defense(self, need_to_protect):
        newest_base = self.enemy_attack_point
        if self.enemy_attack_point == None:
            newest_base = min(self.bases, key = lambda u: u.age)
        self._client.debug_sphere_out(newest_base.position3d, 5, color = Point3((0, 255, 255)))
        self._client.debug_text_world("Queens Defend Here", newest_base.position3d, Point3((0, 255, 255)), 16)
        for queen in self.units().tags_in(self.creep_queens):
            if queen.is_idle and queen.position.distance_to(newest_base) > 6:
                self.do(queen.move(newest_base))
            elif need_to_protect:
                self.do(queen.attack(need_to_protect))

    async def use_queen_transfuse(self):
        low_units = self.units.subgroup(unit for unit in self.units if unit.max_health - unit.health >= 75)
        queens_with_energy = self.units.tags_in(self.creep_queens).subgroup(unit for unit in self.units.tags_in(self.creep_queens) if self.can_cast(unit, AbilityId.TRANSFUSION_TRANSFUSION, only_check_energy_and_cooldown = True))
        for queen in queens_with_energy:
            for unit in low_units:
                if queen.in_ability_cast_range(AbilityId.TRANSFUSION_TRANSFUSION, unit):
                    self.do(queen(AbilityId.TRANSFUSION_TRANSFUSION, unit))
                    low_units.remove(unit)
                    break
    
    async def micro_roach(self, roach):
        if roach.health_percentage < .7 and self.burrow_researched and self.burrow_movement_researched and not roach.is_burrowed:
            self.do(roach(AbilityId.BURROWDOWN_ROACH))
        elif roach.is_burrowed and roach.health_percentage > .9:
            self.do(roach(AbilityId.BURROWUP_ROACH))
        elif roach.is_burrowed:
            self.do(roach.move(Point2(self.rally_point)))
            
    async def micro_mutas(self):
        if len(self.muta_group_tags) == 0:
            self.muta_group_state = MutaGroupState.CONSOLIDATING
            for muta in self.units(MUTALISK):
                self.muta_group_tags.append(muta.tag)
            return
        muta_group = self.units.tags_in(self.muta_group_tags)
        center = muta_group.center
        """
        for muta in self.units.tags_in(self.muta_group_tags):
            if muta.distance_to(center) > 2:
                self.do(muta.move(center))
        """
        if self.muta_group_state == MutaGroupState.CONSOLIDATING:
            # consolidate mutas
            for muta in muta_group:
                if muta.distance_to(self.convert_location(self.army_spot)) > 2:
                    self.do(muta.move(self.convert_location(self.army_spot)))
            if len(muta_group) >= 10:
                ready = True
                for muta in muta_group:
                    if muta.health_percentage < .9 or muta.distance_to(self.convert_location(self.army_spot)) > 2:
                        ready = False
                if ready:
                    self.find_muta_rally_and_attack_points()
                    self.muta_group_state = MutaGroupState.MOVING_TO_RALLY
                    for muta in muta_group:
                        self.do(muta.move(self.muta_rally_point_attack))
                else:
                    # add new mutas
                    for muta in self.units(MUTALISK).tags_not_in(self.muta_group_tags):
                        self.muta_group_tags.append(muta.tag)
            else:
                # add new mutas
                for muta in self.units(MUTALISK).tags_not_in(self.muta_group_tags):
                    self.muta_group_tags.append(muta.tag)
        elif self.muta_group_state == MutaGroupState.MOVING_TO_RALLY:
            if center.distance_to(self.muta_rally_point_attack) < 2:
                if self.muta_attack_point:
                    self.muta_group_state = MutaGroupState.MOVING_TO_ATTACK
                    for muta in muta_group:
                        self.do(muta.move(self.muta_attack_point))
                else:
                    self.muta_group_state = MutaGroupState.RETREATING
                    for muta in muta_group:
                        self.do(muta.move(Point2(self.army_spot)))
        elif self.muta_group_state == MutaGroupState.MOVING_TO_ATTACK:
            if center.distance_to(self.muta_attack_point) < 2:
                self.muta_group_state = MutaGroupState.ATTACKING
        elif self.muta_group_state == MutaGroupState.ATTACKING:
            # when the workers get away, move on
            if len(self.enemy_units({SCV, PROBE, DRONE})) == 0 or self.muta_attack_point.distance_to_closest(self.enemy_units({SCV, PROBE, DRONE})) > 6:
                # TODO if mutas are hurt, retreat them to heal up
                self.find_muta_rally_and_attack_points()
                for muta in muta_group:
                    self.do(muta.move(self.muta_rally_point_attack))
                self.muta_group_state = MutaGroupState.MOVING_TO_RALLY
            else:
                # attack workers
                for muta in muta_group:
                    self.do(muta.attack(self.enemy_units({SCV, PROBE, DRONE}).closest_to(self.muta_attack_point)))
        elif self.muta_group_state == MutaGroupState.RETREATING:
            if center.distance_to(Point2(self.army_spot)) < 2:
                # TODO add new mutas to group
                self.muta_group_state = MutaGroupState.CONSOLIDATING

    def find_muta_rally_and_attack_points(self):
        print("muta find new rally and attack points")
        # new attack point
        if self.muta_attack_point == None:
            if self.enemy_expos[5]:
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[0])
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[6])
            elif self.enemy_expos[4]:
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[5])
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[1])
            elif self.enemy_expos[3]:
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[4])
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[0])
            elif self.enemy_expos[2]:
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[2])
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[4])
            elif self.enemy_expos[1]:
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[3])
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[5])
            elif self.enemy_expos[0]:
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[1])
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[2])
        elif self.muta_attack_point == self.convert_location(self.muta_attack_positions[0]):
            if self.muta_rally_point_attack == self.convert_location(self.muta_rally_points[6]):
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[0])
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[4])
            elif self.muta_rally_point_attack == self.convert_location(self.muta_rally_points[0]):
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[6])
                self.muta_attack_point = None
        elif self.muta_attack_point == self.convert_location(self.muta_attack_positions[4]):
            if self.muta_rally_point_attack == self.convert_location(self.muta_rally_points[0]):
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[5])
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[3])
            elif self.muta_rally_point_attack == self.convert_location(self.muta_rally_points[5]):
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[0])
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[0])
        elif self.muta_attack_point == self.convert_location(self.muta_attack_positions[3]):
            if self.muta_rally_point_attack == self.convert_location(self.muta_rally_points[5]):
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[2])
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[1])
            elif self.muta_rally_point_attack == self.convert_location(self.muta_rally_points[2]):
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[5])
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[4])
        elif self.muta_attack_point == self.convert_location(self.muta_attack_positions[1]):
            if self.muta_rally_point_attack == self.convert_location(self.muta_rally_points[2]):
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[8])
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[6])
            elif self.muta_rally_point_attack == self.convert_location(self.muta_rally_points[8]):
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[2])
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[3])
        elif self.muta_attack_point == self.convert_location(self.muta_attack_positions[6]):
            if self.muta_rally_point_attack == self.convert_location(self.muta_rally_points[8]):
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[4])
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[2])
            elif self.muta_rally_point_attack == self.convert_location(self.muta_rally_points[4]):
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[8])
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[1])
        elif self.muta_attack_point == self.convert_location(self.muta_attack_positions[2]):
            if self.muta_rally_point_attack == self.convert_location(self.muta_rally_points[4]):
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[3])
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[5])
            elif self.muta_rally_point_attack == self.convert_location(self.muta_rally_points[3]):
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[4])
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[6])
        elif self.muta_attack_point == self.convert_location(self.muta_attack_positions[5]):
            if self.muta_rally_point_attack == self.convert_location(self.muta_rally_points[3]):
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[1])
                self.muta_attack_point = None
            elif self.muta_rally_point_attack == self.convert_location(self.muta_rally_points[1]):
                self.muta_rally_point_attack = self.convert_location(self.muta_rally_points[3])
                self.muta_attack_point = self.convert_location(self.muta_attack_positions[2])
    
    async def micro_swarm_hosts(self):
        if len(self.structures(NYDUSNETWORK)) == 0 or len(self.structures(NYDUSCANAL)) == 0:
            return
        if self.swarm_host_state == SwarmHostState.WAITING:
            if self.time - self.last_locust_wave > 43 and len(self.structures(NYDUSNETWORK)[0].passengers) >= 10 and len(self.structures(NYDUSCANAL).ready) > 0:
                self.swarm_host_state = SwarmHostState.UNLOADING
                nydus = self.structures(NYDUSCANAL).ready.random
                self.do(nydus(AbilityId.UNLOADALL_NYDUSWORM))
                self.swarm_host_nydus = nydus.tag
        elif self.swarm_host_state == SwarmHostState.UNLOADING:
            nydus = self.structures.tags_in([self.swarm_host_nydus])[0]
            target = nydus.position.closest(self.enemy_structures({NEXUS, HATCHERY, LAIR, HIVE, COMMANDCENTER, ORBITALCOMMAND, PLANETARYFORTRESS}))
            if not self.structures(NYDUSNETWORK)[0].has_cargo:
                for swarm_host in self.units(SWARMHOSTMP):
                    self.do(swarm_host(AbilityId.EFFECT_SPAWNLOCUSTS, target.position))
                    self.do(swarm_host.smart(nydus, True))
                self.swarm_host_state = SwarmHostState.WAITING
                self.last_locust_wave = self.time
            else:
                self.do(nydus(AbilityId.UNLOADALL_NYDUSWORM))
    
    async def micro_locusts(self):
        for locust in self.units(LOCUSTMPFLYING):
            print("flying locust")
            if len(self.enemy_structures({NEXUS, HATCHERY, LAIR, HIVE, COMMANDCENTER, ORBITALCOMMAND, PLANETARYFORTRESS})) > 0:
                if locust.position.distance_to_closest(self.enemy_structures({NEXUS, HATCHERY, LAIR, HIVE, COMMANDCENTER, ORBITALCOMMAND, PLANETARYFORTRESS})) <= 8:
                    print("swoop")
                    self.do(locust.attack(locust.position.closest(self.enemy_structures({NEXUS, HATCHERY, LAIR, HIVE, COMMANDCENTER, ORBITALCOMMAND, PLANETARYFORTRESS}))))
                else:
                    self.do(locust.move(locust.position.closest(self.enemy_structures({NEXUS, HATCHERY, LAIR, HIVE, COMMANDCENTER, ORBITALCOMMAND, PLANETARYFORTRESS}))))
        
        for locust in self.units(LOCUSTMP):
            if locust.weapon_cooldown == 0:
                print("locust attack")
                workers_in_range = self.enemy_units({SCV, DRONE, PROBE}).in_attack_range_of(locust)
                if len(workers_in_range) > 0:
                    self.do(locust.attack(workers_in_range.random))
                    break
                townhalls_in_range = self.enemy_structures({NEXUS, HATCHERY, LAIR, HIVE, COMMANDCENTER, ORBITALCOMMAND, PLANETARYFORTRESS}).in_attack_range_of(locust)
                if len(townhalls_in_range) > 0:
                    self.do(locust.attack(townhalls_in_range.random))
                    break
                units_in_range = self.enemy_units().in_attack_range_of(locust)
                if len(units_in_range) > 0:
                    self.do(locust.attack(units_in_range.random))
                    break
                buildings_in_range = self.enemy_structures().in_attack_range_of(locust)
                if len(buildings_in_range) > 0:
                    self.do(locust.attack(buildings_in_range.random))
                    break
                # nothing in range
                if len(self.enemy_units({SCV, DRONE, PROBE})) > 0:
                    closest_worker = locust.position.closest(self.enemy_units({SCV, DRONE, PROBE}))
                    if locust.position.distance_to(closest_worker) < 5:
                        self.do(locust.move(closest_worker))
                        break
                if len(self.enemy_structures()) > 0:
                    closest_structure = locust.position.closest(self.enemy_structures())
                    if locust.position.distance_to(closest_structure) < 5:
                        self.do(locust.move(closest_structure))
                        break
                if len(self.enemy_units()) > 0:
                    closest_unit = locust.position.closest(self.enemy_units())
                    if closest_unit:
                        self.do(locust.move(closest_unit))
                        break
                else:
                    locust.move(closest_structure)
            else:
                print("locust move")
                if len(self.enemy_units({SCV, DRONE, PROBE})) > 0:
                    closest_worker = locust.position.closest(self.enemy_units({SCV, DRONE, PROBE}))
                    if locust.position.distance_to(closest_worker) < 5:
                        self.do(locust.move(closest_worker))
                        break
                if len(self.enemy_structures()) > 0:
                    closest_structure = locust.position.closest(self.enemy_structures())
                    if locust.position.distance_to(closest_structure) < 5:
                        self.do(locust.move(closest_structure))
                        break
                if len(self.enemy_units()) > 0:
                    closest_unit = locust.position.closest(self.enemy_units())
                    if closest_unit:
                        self.do(locust.move(closest_unit))
                        break
                else:
                    locust.move(closest_structure)
    
    async def micro_banes(self):
        if self.army_state == ArmyState.ATTACKING or self.army_state == ArmyState.PROTECTING:
            if len(self.units(BANELING)) > 0 and len(self.enemy_units(MARINE)) > 0:
                for baneling in self.units(BANELING):
                    if len(self.enemy_units(MARINE).closer_than(2, baneling.position)) >= 4:
                        self.do(baneling(AbilityId.EXPLODE_EXPLODE))
    
    async def micro_infestors(self):
        print("have infestors")
        if self.army_state == ArmyState.ATTACKING or self.army_state == ArmyState.PROTECTING:
            print("attacking")
            for infestor in self.units(INFESTOR):
                if infestor.energy >= 75:
                    print("have energy")
                    best_value = 5 # minimum 5 units hit
                    best_target = None
                    for target in self.enemy_units:
                        if infestor.in_ability_cast_range(AbilityId.FUNGALGROWTH_FUNGALGROWTH, target):
                            value = len(self.enemy_units.closer_than(2.25, target.position))
                            if value > best_value:
                                best_value = value
                                best_target = target
                                await self.chat_send("better target")
                    if best_target:
                        self._client.debug_line_out(infestor, best_target, color = Point3((255, 0, 0)))
                        self._client.debug_sphere_out(best_target, 2.25, color = Point3((255, 0, 0)))
                        self.do(infestor(AbilityId.FUNGALGROWTH_FUNGALGROWTH, best_target.position))
                    elif len(self.units.tags_in(self.army_unit_tags)) > 0:
                        closest_unit = infestor.position.closest(self.units.tags_in(self.army_unit_tags))
                        self.do(infestor.move(closest_unit))
                elif len(self.units.tags_in(self.army_unit_tags)) > 0:
                    closest_unit = infestor.position.closest(self.units.tags_in(self.army_unit_tags))
                    self.do(infestor.move(closest_unit))
    
    async def micro_vs_proxy(self, unit):
        print(" ")
        proxy_units = self.enemy_units.closer_than(50, self.proxy_location)
        if len(proxy_units) == 0:
            self.do(unit.attack(self.proxy_location))
            print("no enemy units")
            return
        unit_prio = [MARINE, SCV]
        if unit.weapon_cooldown == 0:
            for unit_type in unit_prio:
                attackable_units = proxy_units(unit_type).in_attack_range_of(unit)
                if len(attackable_units) > 0:
                    self.do(unit.attack(attackable_units[0]))
                    self._client.debug_line_out(unit, attackable_units[0], color = Point3((255, 0, 0)))
                    print(str(unit) + " attack " + str(attackable_units[0]))
                    return
            print("nothing in range")
            # no units in range
            for unit_type in unit_prio:
                nearby_units = proxy_units(unit_type).sorted_by_distance_to(unit.position)
                if len(nearby_units) > 0:
                    self.do(unit.attack(nearby_units[0]))
                    self._client.debug_line_out(unit, nearby_units[0], color = Point3((0, 255, 0)))
                    print(str(unit) + " move to " + str(nearby_units[0]))
                    return
            print("shouldnt be here")
        else:
            print("weapon on cooldown")
            for unit_type in unit_prio:
                nearby_units = proxy_units(unit_type).sorted_by_distance_to(unit.position)
                if len(nearby_units) > 0:
                    self.do(unit.attack(nearby_units[0]))
                    self._client.debug_line_out(unit, nearby_units[0], color = Point3((0, 0, 255)))
                    print(str(unit) + " move 2 " + str(nearby_units[0]))
                    return
            print("shouldnt be here either")
        
    async def deny_proxy(self):
        if self.enemy_race == Race.Terran:
            if self.proxy_status == ProxyStatus.PR_RAX_STARTED:
                scvs = [unit for unit in self.proxy_units if unit[1] == SCV]
                if len(scvs) > 0:
                    # pull more drones if neccessary
                    new_drones_needed = len(scvs) * 2 - len(self.pulled_worker_tags)
                    if new_drones_needed > 0:
                        await self.chat_send("need " + str(new_drones_needed) + " more drones")
                        for drone in self.units(DRONE).tags_not_in(self.pulled_worker_tags).closest_n_units(self.proxy_location, new_drones_needed):
                            self.pulled_worker_tags.append(drone.tag)
                    if len(self.pulled_worker_tags) > 0:
                        for drone in self.units.tags_in(self.pulled_worker_tags):
                            await self.micro_vs_proxy(drone)
                else:
                    # once all scvs are dead withdraw the pulled drones
                    self.pulled_worker_tags = []
                
                if len(self.units(ZERGLING).ready) > 0:
                    for ling in self.units(ZERGLING).ready:
                        await self.micro_vs_proxy(ling)
                     
            elif self.proxy_status == ProxyStatus.PR_SOME_RAX_FINISHED:
                # withdraw injured drones
                drones = self.units.tags_in(self.pulled_worker_tags)
                escape_target = None
                if self.structures(EXTRACTOR):
                    escape_target = self.structures(EXTRACTOR).ready.random
                else:
                    escape_target = self.all_units().is_mineral_field.closest_to(self.start_location)
                for drone in drones:
                    if drone.health <= 15:
                        self.do(drone.smart(escape_target))
                        self.pulled_worker_tags.remove(drone.tag)
                
                num_barracks = len([building for building in self.proxy_buildings if building[1] == BARRACKS])
                for drone in self.units(DRONE).tags_not_in(self.pulled_worker_tags):
                    if len(self.pulled_worker_tags) >= 4 * num_barracks:
                        break;
                    if drone.health >= 40:
                        self.pulled_worker_tags.append(drone.tag)
                
                for ling in self.units(ZERGLING).ready:
                    if ling.distance_to(self.proxy_location) > 10:
                        self.do(ling.move(self.units.tags_in(self.pulled_worker_tags).center))
                    else:
                        await self.micro_vs_proxy(ling)
                for drone in self.units.tags_in(self.pulled_worker_tags):
                    await self.micro_vs_proxy(drone)
                
            elif self.proxy_status == ProxyStatus.PR_ALL_RAX_FINISHED:
                # withdraw injured drones
                drones = self.units.tags_in(self.pulled_worker_tags)
                escape_target = None
                if self.structures(EXTRACTOR):
                    escape_target = self.structures(EXTRACTOR).ready.random
                else:
                    escape_target = self.all_units().is_mineral_field.closest_to(self.start_location)
                for drone in drones:
                    if drone.health <= 15:
                        self.do(drone.smart(escape_target))
                        self.pulled_worker_tags.remove(drone.tag)
                
                num_barracks = len([building for building in self.proxy_buildings if building[1] == BARRACKS])
                for drone in self.units(DRONE).tags_not_in(self.pulled_worker_tags):
                    if len(self.pulled_worker_tags) >= 4 * num_barracks:
                        break;
                    if drone.health >= 40:
                        self.pulled_worker_tags.append(drone.tag)
                
                for ling in self.units(ZERGLING).ready:
                    if ling.distance_to(self.proxy_location) > 10:
                        self.do(ling.move(self.units.tags_in(self.pulled_worker_tags).center))
                    else:
                        await self.micro_vs_proxy(ling)
                for drone in self.units.tags_in(self.pulled_worker_tags):
                    await self.micro_vs_proxy(drone)
                
            """elif self.proxy_status == ProxyStatus.PR_UNPROTECTED_BUNKER:
                
            elif self.proxy_status == ProxyStatus.PR_PROTECTED_BUNKER:
                
            elif self.proxy_status == ProxyStatus.PR_NO_BUNKER_ATTACK:
                
            elif self.proxy_status == ProxyStatus.PR_BUNKER_FINISHED:"""
                
            
    
    async def enter_pr_rax_started(self):
        if self.units(ZERGLING).ready:
            for ling in self.units(ZERGLING).ready:
                self.do(ling.attack(self.proxy_location))
        else:
            rax = len(self.enemy_structures(BARRACKS)) + 1
            for drone in self.units(DRONE).closest_n_units(self.proxy_location, rax):
                self.pulled_worker_tags.append(drone.tag)
                self.do(drone.attack(self.proxy_location))
    
    async def enter_pr_some_rax_finished(self):
        # unused for now
        return
                    
    async def enter_pr_all_rax_finished(self):
        # unused for now
        return 
    
                    
    
########################################
################# MACRO ################
########################################

    async def build_roach_warren(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.build_location = None
            self.builder_drone = self.select_build_worker(self.start_location).tag
            self.remove_drone(self.builder_drone)
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
        elif self.build_location == None:
            print("no place")
            builder = self.units.tags_in([self.builder_drone])[0]
            pool_location = self.structures(SPAWNINGPOOL)[0].position
            self.build_location = await self.find_placement(UnitTypeId.ROACHWARREN, near = pool_location, max_distance = 6)
            if self.build_location != None and not await self.can_place_single(ROACHWARREN, self.build_location):
                self.build_location = None
        #elif not await self.can_place(ROACHWARREN, self.build_location):
            #print("invalid place")
            #self.build_location = None
        elif await self.can_place_single(ROACHWARREN, self.build_location):
            builder = self.units.tags_in([self.builder_drone])[0]
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.build(ROACHWARREN, self.build_location))
        
    
    async def build_baneling_nest(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.build_location = None
            self.builder_drone = self.select_build_worker(self.start_location).tag
            self.remove_drone(self.builder_drone)
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
        elif self.build_location == None:
            print("no place")
            builder = self.units.tags_in([self.builder_drone])[0]
            pool_location = self.structures(SPAWNINGPOOL)[0].position
            self.build_location = await self.find_placement(UnitTypeId.BANELINGNEST, near = pool_location, max_distance = 6)
            if self.build_location != None and not await self.can_place_single(ROACHWARREN, self.build_location):
                self.build_location = None
        #elif not await self.can_place(BANELINGNEST, self.build_location):
            #print("invalid place")
            #self.build_location = None
        elif await self.can_place_single(BANELINGNEST, self.build_location):
            builder = self.units.tags_in([self.builder_drone])[0]
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.build(BANELINGNEST, self.build_location))
    
    async def build_evolution_chamber(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.build_location = None
            self.builder_drone = self.select_build_worker(self.start_location).tag
            self.remove_drone(self.builder_drone)
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
        elif self.build_location == None:
            print("no place")
            builder = self.units.tags_in([self.builder_drone])[0]
            pool_location = self.structures(SPAWNINGPOOL)[0].position
            self.build_location = await self.find_placement(UnitTypeId.EVOLUTIONCHAMBER, near = pool_location, max_distance = 6)
            if self.build_location != None and not await self.can_place_single(ROACHWARREN, self.build_location):
                self.build_location = None
        #elif not await self.can_place(EVOLUTIONCHAMBER, self.build_location):
            #print("invalid place")
            #self.build_location = None
        elif await self.can_place_single(EVOLUTIONCHAMBER, self.build_location):
            builder = self.units.tags_in([self.builder_drone])[0]
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.build(EVOLUTIONCHAMBER, self.build_location))
            
    async def build_hydralisk_den(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.build_location = None
            self.builder_drone = self.select_build_worker(self.start_location).tag
            self.remove_drone(self.builder_drone)
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
        elif self.build_location == None:
            print("no place")
            builder = self.units.tags_in([self.builder_drone])[0]
            pool_location = self.structures(SPAWNINGPOOL)[0].position
            self.build_location = await self.find_placement(UnitTypeId.HYDRALISKDEN, near = pool_location, max_distance = 6)
            if self.build_location != None and not await self.can_place_single(HYDRALISKDEN, self.build_location):
                self.build_location = None
        #elif not await self.can_place(HYDRALISKDEN, self.build_location):
            #print("invalid place")
            #self.build_location = None
        elif await self.can_place_single(HYDRALISKDEN, self.build_location):
            builder = self.units.tags_in([self.builder_drone])[0]
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.build(HYDRALISKDEN, self.build_location))
            
    async def build_infestation_pit(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.build_location = None
            self.builder_drone = self.select_build_worker(self.start_location).tag
            self.remove_drone(self.builder_drone)
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
        elif self.build_location == None:
            print("no place")
            builder = self.units.tags_in([self.builder_drone])[0]
            pool_location = self.structures(SPAWNINGPOOL)[0].position
            self.build_location = await self.find_placement(UnitTypeId.INFESTATIONPIT, near = pool_location, max_distance = 6)
            if self.build_location != None and not await self.can_place_single(INFESTATIONPIT, self.build_location):
                self.build_location = None
        #elif not await self.can_place(INFESTATIONPIT, self.build_location):
            #print("invalid place")
            #self.build_location = None
        elif await self.can_place_single(INFESTATIONPIT, self.build_location):
            builder = self.units.tags_in([self.builder_drone])[0]
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.build(INFESTATIONPIT, self.build_location))
             
    async def build_spire(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.build_location = None
            self.builder_drone = self.select_build_worker(self.start_location).tag
            self.remove_drone(self.builder_drone)
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
        elif self.build_location == None:
            print("no place")
            builder = self.units.tags_in([self.builder_drone])[0]
            pool_location = self.structures(SPAWNINGPOOL)[0].position
            self.build_location = await self.find_placement(UnitTypeId.SPIRE, near = pool_location, max_distance = 6)
            if self.build_location != None and not await self.can_place_single(SPIRE, self.build_location):
                self.build_location = None
        #elif not await self.can_place(SPIRE, self.build_location):
            #print("invalid place")
            #self.build_location = None
        elif await self.can_place_single(SPIRE, self.build_location):
            builder = self.units.tags_in([self.builder_drone])[0]
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.build(SPIRE, self.build_location))
            
    async def build_gas(self):
        print("build gas??")
        if self.minerals >= 25:
            print("build gas")
            for hatch in self.structures({HATCHERY, LAIR, HIVE}).ready:
                vespenes = self.vespene_geyser.closer_than(10.0, hatch)
                for vespene in vespenes:
                    worker = self.select_build_worker(vespene.position)
                    self.remove_drone(worker.tag)
                    if worker is None:
                        break
                    self._client.debug_sphere_out(Point3((vespene.position[0], vespene.position[1], self.get_terrain_z_height(vespene.position))), 1, color = Point3((255, 255, 0)))
                    self.do(worker.build(EXTRACTOR, vespene))
                    return True
        return False
    
    async def build_nydus_network(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.build_location = None
            self.builder_drone = self.select_build_worker(self.start_location).tag
            self.remove_drone(self.builder_drone)
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
        elif self.build_location == None:
            print("no place")
            builder = self.units.tags_in([self.builder_drone])[0]
            pool_location = self.structures(SPAWNINGPOOL)[0].position
            self.build_location = await self.find_placement(UnitTypeId.NYDUSNETWORK, near = pool_location, max_distance = 6)
            if self.build_location != None and not await self.can_place_single(NYDUSNETWORK, self.build_location):
                self.build_location = None
        #elif not await self.can_place(NYDUSNETWORK, self.build_location):
            #print("invalid place")
            #self.build_location = None
        elif await self.can_place_single(NYDUSNETWORK, self.build_location):
            builder = self.units.tags_in([self.builder_drone])[0]
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.build(NYDUSNETWORK, self.build_location))
            
    """
    async def use_larva(self):
        # are any buildings needed
        if self.expansion_need == 100 or self.pending_upgrade == 1:
            return
        
        await self.update_units_needs()
        if len(self.units(QUEEN)) + self.already_pending(QUEEN) < self.queen_need:
            if self.minerals >= 150:
                await self.build_queen()
        all_larva = self.units(LARVA)
        if len(all_larva) == 0:
            return
        for larva in all_larva:
            #don't get supply blocked
            if self.supply_cap < 200 and ((self.supply_used / self.supply_cap >= .8 and not self.already_pending(OVERLORD) > 0) or (self.supply_used / self.supply_cap >= .9 and not self.already_pending(OVERLORD) > 1)):
                if self.minerals >= 100:
                    self.do(larva.train(OVERLORD))
            elif self.supply_workers + self.already_pending(DRONE) < self.drone_need:
                if self.minerals >= 50:
                    self.do(larva.train(DRONE))
            elif len(self.units(ZERGLING)) + self.already_pending(ZERGLING) + len(self.units(BANELING)) + self.already_pending(BANELING) < self.zergling_need:
                if self.minerals >= 50:
                    self.do(larva.train(ZERGLING))
            elif len(self.units(ROACH)) + self.already_pending(ROACH) < self.roach_need and self.pending_upgrade != 2:
                if self.minerals >= 75 and self.vespene >= 25:
                    self.do(larva.train(ROACH))
            elif len(self.units(HYDRALISK)) + self.already_pending(HYDRALISK) < self.hydralisk_need and self.pending_upgrade != 2:
                if self.minerals >= 100 and self.vespene >= 50:
                    self.do(larva.train(HYDRALISK))
            elif len(self.units(MUTALISK)) + self.already_pending(MUTALISK) < self.mutalisk_need and self.pending_upgrade != 2:
                if self.minerals >= 100 and self.vespene >= 100:
                    self.do(larva.train(MUTALISK))
            elif len(self.units(INFESTOR)) + self.already_pending(INFESTOR) < self.infestor_need and self.pending_upgrade != 2:
                if self.minerals >= 100 and self.vespene >= 150:
                    self.do(larva.train(INFESTOR))
            elif len(self.structures(NYDUSNETWORK).ready) and len(self.structures(NYDUSNETWORK)[0].passengers) + len(self.units(SWARMHOSTMP)) + self.already_pending(SWARMHOSTMP) < self.swarmhost_need and self.pending_upgrade != 2:
                if self.minerals >= 100 and self.vespene >= 75:
                    self.do(larva.train(SWARMHOSTMP))
            elif len(self.units(SWARMHOSTMP)) + self.already_pending(SWARMHOSTMP) < self.swarmhost_need and self.pending_upgrade != 2:
                if self.minerals >= 100 and self.vespene >= 75:
                    self.do(larva.train(SWARMHOSTMP))
        if self.pending_upgrade != 2:
            for zergling in self.units(ZERGLING).idle:
                if len(self.units(BANELING)) + self.already_pending(BANELING) < self.baneling_need:
                    if self.minerals >= 25 and self.vespene >= 25:
                        self.do(zergling(AbilityId.MORPHZERGLINGTOBANELING_BANELING))

    async def make_expansions(self):
        if self.expansion_need == 100:
            if self.minerals >= 300:
                self.last_expansion_time = self.time
                expansion_location = await self.get_next_expansion()
                builder_drone = self.select_build_worker(expansion_location)
                self.remove_drone(builder_drone.tag)
                self.do(builder_drone.build(HATCHERY, expansion_location))
        """
        
            
    async def expand_tech(self):
        if self.time >= 240:
            await self.build_extractor()
            if self.army_composition == ArmyComp.LING_BANE_HYDRA or self.army_composition == ArmyComp.LING_BANE_MUTA:
                if self.can_afford(BANELINGNEST) and len(self.structures(BANELINGNEST)) == 0:
                    await self.build_baneling_nest()
            elif self.army_composition == ArmyComp.ROACH_HYDRA or self.army_composition == ArmyComp.ROACH_SWARM_HOST:
                if self.can_afford(ROACHWARREN) and len(self.structures(ROACHWARREN)) == 0:
                    await self.build_roach_warren()
        if self.supply_workers > 40 or self.time > 240:
            await self.build_spores()
            if len(self.structures(LAIR)) + len(self.structures(HIVE)) == 0 and not self.already_pending(LAIR):
                hatch = self.structures(HATCHERY)[0]
                for ability in await self.get_available_abilities(hatch):
                    if ability == AbilityId.UPGRADETOLAIR_LAIR:
                        self.do(hatch(AbilityId.UPGRADETOLAIR_LAIR))
        if self.supply_workers > 80 or self.time > 480:
            if len(self.structures(HIVE)) == 0 and not self.already_pending(HIVE) and len(self.structures(LAIR)) > 0:
                hatch = self.structures(LAIR)[0]
                for ability in await self.get_available_abilities(hatch):
                    if ability == AbilityId.UPGRADETOHIVE_HIVE:
                        self.do(hatch(AbilityId.UPGRADETOHIVE_HIVE))
        if len(self.structures(LAIR)) > 0 or self.already_pending(LAIR):
            if self.can_afford(EVOLUTIONCHAMBER) and len(self.structures(EVOLUTIONCHAMBER)) < 2:
                await self.build_evolution_chamber()
        if len(self.structures(LAIR)) > 0:
            if  self.army_composition == ArmyComp.LING_BANE_HYDRA or self.army_composition == ArmyComp.ROACH_HYDRA:
                if self.can_afford(HYDRALISKDEN) and len(self.structures(HYDRALISKDEN)) == 0:
                    await self.build_hydralisk_den()
                if self.can_afford(INFESTATIONPIT) and len(self.structures(INFESTATIONPIT)) == 0 and self.time > 300 and len(self.structures(HYDRALISKDEN)) > 0:
                    await self.build_infestation_pit()
            elif self.army_composition == ArmyComp.LING_BANE_MUTA:
                if self.can_afford(SPIRE) and len(self.structures({SPIRE, GREATERSPIRE})) == 0:
                    await self.build_spire()
                    
            elif  self.army_composition == ArmyComp.ROACH_SWARM_HOST and len(self.townhalls.ready) >= 3:
                if self.can_afford(INFESTATIONPIT) and len(self.structures(INFESTATIONPIT)) == 0:
                    await self.build_infestation_pit()
                if self.can_afford(NYDUSNETWORK) and len(self.structures(NYDUSNETWORK)) == 0:
                    await self.build_nydus_network()
    
    async def build_extractor(self):
        if self.vespene > 500 or (self.time < 360 and len(self.structures(EXTRACTOR)) >= 2):
            return
        for hatch in self.structures({HATCHERY, LAIR, HIVE}).ready:
            if hatch.assigned_harvesters > hatch.ideal_harvesters - 2 or (self.vespene < 100 and self.already_pending(EXTRACTOR) < 2):
                vespenes = self.vespene_geyser.closer_than(10.0, hatch)
                for vespene in vespenes:
                    if self.can_afford(EXTRACTOR) and not self.structures(EXTRACTOR).closer_than(1.0, vespene).exists:
                        worker = self.select_build_worker(vespene.position)
                        self.remove_drone(worker.tag)
                        if worker is None:
                            break
                        self.do(worker.build(EXTRACTOR, vespene))

    async def inject_larva(self):
        for queen in self.units(QUEEN):
            if queen.tag in self.injecting_queens:
                self._client.debug_sphere_out(queen.position3d, 2, color = Point3((0, 0, 255)))
                hatches = self.structures({HATCHERY, LAIR, HIVE}).sorted_by_distance_to(queen.position3d)
                for hatch in hatches:
                    if hatch == hatches[0]:
                        self._client.debug_line_out(queen, hatch, color = Point3((0, 255, 0)))
                    else:
                        self._client.debug_line_out(queen, hatch, color = Point3((255, 0, 0)))
                if queen.energy >= 25 and not queen.is_active:
                    hatchery = self.townhalls._list_sorted_by_distance_to(queen)[0]
                    if not hatchery.has_buff(BuffId.QUEENSPAWNLARVATIMER):
                        self.do(queen(AbilityId.EFFECT_INJECTLARVA, hatchery))
    
    async def get_upgrades(self):
        # melee
        if self.army_composition == ArmyComp.LING_BANE_HYDRA or self.army_composition == ArmyComp.LING_BANE_MUTA:
            if self.structures(EVOLUTIONCHAMBER).ready.idle and not self.already_pending_upgrade(UpgradeId.ZERGMELEEWEAPONSLEVEL1):
                if self.can_afford(UpgradeId.ZERGMELEEWEAPONSLEVEL1):
                    evo = self.structures(EVOLUTIONCHAMBER).ready.idle.random
                    self.do(evo(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL1))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL1).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
            elif self.structures(EVOLUTIONCHAMBER).ready.idle and not self.already_pending_upgrade(UpgradeId.ZERGMELEEWEAPONSLEVEL2) and len(self.structures({LAIR, HIVE})) > 0:
                if self.can_afford(UpgradeId.ZERGMELEEWEAPONSLEVEL2):
                    evo = self.structures(EVOLUTIONCHAMBER).ready.idle.random
                    self.do(evo(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
            elif self.structures(EVOLUTIONCHAMBER).ready.idle and not self.already_pending_upgrade(UpgradeId.ZERGMELEEWEAPONSLEVEL3) and len(self.structures(HIVE)) > 0:
                if self.can_afford(UpgradeId.ZERGMELEEWEAPONSLEVEL3):
                    evo = self.structures(EVOLUTIONCHAMBER).ready.idle.random
                    self.do(evo(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
    
        # missile
        if self.army_composition == ArmyComp.LING_BANE_HYDRA or self.army_composition == ArmyComp.ROACH_HYDRA or self.army_composition == ArmyComp.ROACH_SWARM_HOST:
            if self.structures(EVOLUTIONCHAMBER).ready.idle and not self.already_pending_upgrade(UpgradeId.ZERGMISSILEWEAPONSLEVEL1):
                if self.can_afford(UpgradeId.ZERGMISSILEWEAPONSLEVEL1):
                    evo = self.structures(EVOLUTIONCHAMBER).ready.idle.random
                    self.do(evo(AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
            elif self.structures(EVOLUTIONCHAMBER).ready.idle and not self.already_pending_upgrade(UpgradeId.ZERGMISSILEWEAPONSLEVEL2) and len(self.structures({LAIR, HIVE})) > 0:
                if self.can_afford(UpgradeId.ZERGMISSILEWEAPONSLEVEL2):
                    evo = self.structures(EVOLUTIONCHAMBER).ready.idle.random
                    self.do(evo(AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
            elif self.structures(EVOLUTIONCHAMBER).ready.idle and not self.already_pending_upgrade(UpgradeId.ZERGMISSILEWEAPONSLEVEL3) and len(self.structures(HIVE)) > 0:
                if self.can_afford(UpgradeId.ZERGMISSILEWEAPONSLEVEL3):
                    evo = self.structures(EVOLUTIONCHAMBER).ready.idle.random
                    self.do(evo(AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL3))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL3).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
                
        # armor
        if self.army_composition == ArmyComp.ROACH_HYDRA:
            if self.structures(EVOLUTIONCHAMBER).ready.idle and not self.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL1):
                if self.can_afford(UpgradeId.ZERGGROUNDARMORSLEVEL1):
                    evo = self.structures(EVOLUTIONCHAMBER).ready.idle.random
                    self.do(evo(AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
            elif self.structures(EVOLUTIONCHAMBER).ready.idle and not self.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL2) and len(self.structures({LAIR, HIVE})) > 0:
                if self.can_afford(UpgradeId.ZERGGROUNDARMORSLEVEL2):
                    evo = self.structures(EVOLUTIONCHAMBER).ready.idle.random
                    self.do(evo(AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
            elif self.structures(EVOLUTIONCHAMBER).ready.idle and not self.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL3) and len(self.structures(HIVE)) > 0:
                if self.can_afford(UpgradeId.ZERGGROUNDARMORSLEVEL3):
                    evo = self.structures(EVOLUTIONCHAMBER).ready.idle.random
                    self.do(evo(AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
        
        # zergling
        if self.army_composition == ArmyComp.LING_BANE_HYDRA or self.army_composition == ArmyComp.LING_BANE_MUTA:
            if self.structures(SPAWNINGPOOL).ready.idle and not self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED):
                if self.can_afford(UpgradeId.ZERGLINGMOVEMENTSPEED):
                    pool = self.structures(SPAWNINGPOOL).ready.idle.random
                    self.do(pool(AbilityId.RESEARCH_ZERGLINGMETABOLICBOOST))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_ZERGLINGMETABOLICBOOST).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
            elif self.structures(SPAWNINGPOOL).ready.idle and not self.already_pending_upgrade(UpgradeId.ZERGLINGATTACKSPEED) and len(self.structures(HIVE)) > 0:
                if self.can_afford(UpgradeId.ZERGLINGATTACKSPEED):
                    pool = self.structures(SPAWNINGPOOL).ready.idle.random
                    self.do(pool(AbilityId.RESEARCH_ZERGLINGADRENALGLANDS))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_ZERGLINGADRENALGLANDS).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
        # baneling
        if self.army_composition == ArmyComp.LING_BANE_HYDRA or self.army_composition == ArmyComp.LING_BANE_MUTA:
            if self.structures(BANELINGNEST).ready.idle and not self.already_pending_upgrade(UpgradeId.CENTRIFICALHOOKS) and len(self.structures({LAIR, HIVE})) > 0:
                if self.can_afford(UpgradeId.CENTRIFICALHOOKS):
                    bane = self.structures(BANELINGNEST).ready.idle.random
                    self.do(bane(AbilityId.RESEARCH_CENTRIFUGALHOOKS))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_CENTRIFUGALHOOKS).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2

        # roach
        if self.army_composition == ArmyComp.ROACH_HYDRA or self.army_composition == ArmyComp.ROACH_SWARM_HOST:
            if self.structures(ROACHWARREN).ready.idle and not self.already_pending_upgrade(UpgradeId.GLIALRECONSTITUTION) and len(self.structures({LAIR, HIVE})) > 0:
                if self.can_afford(UpgradeId.GLIALRECONSTITUTION):
                    roach_warren = self.structures(ROACHWARREN).ready.idle.random
                    self.do(roach_warren(AbilityId.RESEARCH_GLIALREGENERATION))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_GLIALREGENERATION).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
            elif self.structures(ROACHWARREN).ready.idle and not self.already_pending_upgrade(UpgradeId.TUNNELINGCLAWS) and len(self.structures({LAIR, HIVE})) > 0:
                if self.can_afford(UpgradeId.TUNNELINGCLAWS):
                    roach_warren = self.structures(ROACHWARREN).ready.idle.random
                    self.do(roach_warren(AbilityId.RESEARCH_TUNNELINGCLAWS))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_TUNNELINGCLAWS).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
        
        # hydra
        if self.army_composition == ArmyComp.LING_BANE_HYDRA or self.army_composition == ArmyComp.ROACH_HYDRA:
            if self.structures(HYDRALISKDEN).ready.idle and not self.already_pending_upgrade(UpgradeId.EVOLVEMUSCULARAUGMENTS) and len(self.structures({LAIR, HIVE})) > 0:
                if self.can_afford(UpgradeId.EVOLVEMUSCULARAUGMENTS):
                    hydra_den = self.structures(HYDRALISKDEN).ready.idle.random
                    self.do(hydra_den(AbilityId.RESEARCH_MUSCULARAUGMENTS))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_MUSCULARAUGMENTS).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
            elif self.structures(HYDRALISKDEN).ready.idle and not self.already_pending_upgrade(UpgradeId.EVOLVEGROOVEDSPINES) and len(self.structures({LAIR, HIVE})) > 0:
                if self.can_afford(UpgradeId.EVOLVEGROOVEDSPINES):
                    hydra_den = self.structures(HYDRALISKDEN).ready.idle.random
                    self.do(hydra_den(AbilityId.RESEARCH_GROOVEDSPINES))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_GROOVEDSPINES).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
        
        # spire
        if self.army_composition == ArmyComp.LING_BANE_MUTA:
            if self.structures({SPIRE, GREATERSPIRE}).ready.idle and not self.already_pending_upgrade(UpgradeId.ZERGFLYERWEAPONSLEVEL1):
                if self.can_afford(UpgradeId.ZERGFLYERWEAPONSLEVEL1):
                    spire = self.structures({SPIRE, GREATERSPIRE}).ready.idle.random
                    self.do(spire(AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL1))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL1).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
            elif self.structures({SPIRE, GREATERSPIRE}).ready.idle and not self.already_pending_upgrade(UpgradeId.ZERGFLYERWEAPONSLEVEL2) and len(self.structures({LAIR, HIVE})) > 0:
                if self.can_afford(UpgradeId.ZERGFLYERWEAPONSLEVEL2):
                    spire = self.structures({SPIRE, GREATERSPIRE}).ready.idle.random
                    self.do(spire(AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL2))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL2).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
            elif self.structures({SPIRE, GREATERSPIRE}).ready.idle and not self.already_pending_upgrade(UpgradeId.ZERGFLYERWEAPONSLEVEL3) and len(self.structures(HIVE)) > 0:
                if self.can_afford(UpgradeId.ZERGFLYERWEAPONSLEVEL3):
                    spire = self.structures({SPIRE, GREATERSPIRE}).ready.idle.random
                    self.do(spire(AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL3))
                    self.pending_upgrade = 0
                elif self.calculate_cost(AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL3).minerals > self.minerals:
                    self.pending_upgrade = 1
                else:
                    self.pending_upgrade = 2
        

        # hatchery
        if self.structures({HATCHERY, LAIR, HIVE}).ready.idle and not self.already_pending_upgrade(UpgradeId.OVERLORDSPEED) and self.time > 300:
            if self.can_afford(UpgradeId.OVERLORDSPEED):
                hatch = self.structures({HATCHERY, LAIR, HIVE}).ready.idle.random
                if hatch == self.structures({HATCHERY, LAIR, HIVE})[0]:
                    hatch = self.structures({HATCHERY, LAIR, HIVE}).ready.idle.random
                self.do(hatch(AbilityId.RESEARCH_PNEUMATIZEDCARAPACE))
                self.pending_upgrade = 0
            elif self.calculate_cost(AbilityId.RESEARCH_PNEUMATIZEDCARAPACE).minerals > self.minerals:
                self.pending_upgrade = 1
            else:
                self.pending_upgrade = 2
        elif self.structures({HATCHERY, LAIR, HIVE}).ready.idle and not self.already_pending_upgrade(UpgradeId.BURROW) and self.time > 300:
            if self.can_afford(UpgradeId.BURROW):
                hatch = self.structures({HATCHERY, LAIR, HIVE}).ready.idle.random
                if hatch == self.structures({HATCHERY, LAIR, HIVE})[0]:
                    hatch = self.structures({HATCHERY, LAIR, HIVE}).ready.idle.random
                self.do(hatch(AbilityId.RESEARCH_BURROW))
                self.pending_upgrade = 0
            elif self.calculate_cost(AbilityId.RESEARCH_BURROW).minerals > self.minerals:
                self.pending_upgrade = 1
            else:
                self.pending_upgrade = 2
    
    async def build_spores(self):
        #if self.spore_need == 100:
        for spore_pos in self.spore_positions:
            pos = self.convert_location(spore_pos)
            if self.minerals > 150 and pos.distance_to_closest(self.townhalls.ready) < 10 and self.has_creep(pos):
                if len(self.structures(SPORECRAWLER)) == 0 or pos.distance_to_closest(self.structures(SPORECRAWLER)) > 2:
                    drone = pos.closest(self.units(DRONE))
                    self.remove_drone(drone.tag)
                    self.do(drone.build(SPORECRAWLER, pos))
                        
    

########################################
################ UTILITY ###############
########################################
    
    async def display_debug_info(self):
        for i in range(0, len(self.spore_positions)):
            pos = self.convert_location(self.spore_positions[i])
            height = self.get_terrain_z_height(Point2(pos))
            self._client.debug_sphere_out(Point3((pos[0], pos[1], height)), 1, color = Point3((255, 255, 0)))
            self._client.debug_text_world("spore " + str(i), Point3((pos[0], pos[1], height)), Point3((255, 255, 0)), 16)
        
        if not self.has_debug and round(self.time) % self.debug_interval == 0:
            self.has_debug = True
            print("START DEBUG")
            print(str(self.time_formatted))
            print(str(self.enemy_unit_numbers))
            if self.army_composition == ArmyComp.LING_BANE_HYDRA:
                print("ling need: " + str(self.zergling_need))
                print("bane need: " + str(self.baneling_need))
                print("hydra need: " + str(self.hydralisk_need))
            elif self.army_composition == ArmyComp.LING_BANE_MUTA:
                print("ling need: " + str(self.zergling_need))
                print("bane need: " + str(self.baneling_need))
                print("muta in group: " + str(len(self.muta_group_tags)))
                print("muta status: " + str(self.muta_group_state))
            elif self.army_composition == ArmyComp.ROACH_HYDRA:
                print("roach need: " + str(self.roach_need))
                print("hydra need: " + str(self.hydralisk_need))
            elif self.army_composition == ArmyComp.ROACH_SWARM_HOST:
                print("roach need: " + str(self.roach_need))
                print("swarm host need: " + str(self.swarmhost_need))
            if self.expansion_need == 100:
                print("need to expand")
            else:
                print("enemy bases "  + str(sum(self.enemy_expos) + 1) + " my bases " + str(len(self.townhalls)))
                print("next expo: " + str(self.last_expansion_time + 120) + " time " + str(self.time))
            
            print(self.proxy_status.name)
            print(self.proxy_units)
            print(self.proxy_buildings)
            print("END DEBUG")
        elif self.has_debug and round(self.time) % self.debug_interval == 1:
            self.has_debug = False
    
    def set_up_map_graph(self):
        for index, point in enumerate(self.army_positions):
            self.army_positions[index] = self.convert_location(point)
        for i in range(0, len(self.army_position_links)):
            for j in range(0, len(self.army_position_links[i])):
                self.map_graph.add_edge(i, self.army_position_links[i][j], Point2(self.army_positions[i]).distance_to(Point2(self.army_positions[self.army_position_links[i][j]])))
        
    def update_unit_tags(self):
        self.tag_to_unit.clear()
        for unit in self.all_units:
            self.tag_to_unit[unit.tag] = unit

    async def on_unit_created(self, unit):
        if unit.type_id == QUEEN:
            if len(self.injecting_queens) > len(self.creep_queens):
                self.creep_queens.append(unit.tag)
            else:
                self.injecting_queens.append(unit.tag)
            self.spread_inject_queens()
        elif unit.type_id == OVERLORD:
            self.position_new_overlord(unit)
        elif unit.type_id == ZERGLING:
            for i in range(0, len(self.zergling_scout_tags)):
                if self.zergling_scout_tags[i] == None:
                    self.zergling_scout_tags[i] = unit.tag
                    break
        elif unit.type_id == SWARMHOSTMP:
            self.do(unit.smart(self.structures(NYDUSNETWORK)[0]))
        elif unit.type_id == DRONE:
            self.place_drone(unit)
    
    async def on_building_construction_complete(self, building):
        if building.type_id == UnitTypeId.HATCHERY:
            self.spread_inject_queens()
            self.bases.append(building)
            self.add_new_base = building.tag
        elif building.type_id == UnitTypeId.NYDUSNETWORK:
            for swarm_host in self.units(SWARMHOSTMP):
                self.do(swarm_host.smart(building))
        elif building.type_id == UnitTypeId.EXTRACTOR:
            self.extractors[building.tag] = (None, None, None)
    
    async def on_building_construction_started(self, unit):
        if unit.type_id == UnitTypeId.HATCHERY:
            self.last_expansion_time = self.time
            await self.chat_send("Next expo at: " + str(math.floor((self.time + 120) / 60)) + ":" + str(math.floor((self.time + 120) % 60)))
            
    async def on_upgrade_complete(self, upgrade):
        if upgrade == UpgradeId.BURROW:
            self.burrow_researched = True
        elif upgrade == UpgradeId.TUNNELINGCLAWS:
            self.burrow_movement_researched = True

    async def on_unit_destroyed(self, unit_tag):
        if unit_tag in self.enemy_unit_tags.keys():
            #print("-1 " + str(self.enemy_unit_tags[unit_tag]))
            self.enemy_unit_numbers[self.enemy_unit_tags[unit_tag]] = self.enemy_unit_numbers[self.enemy_unit_tags[unit_tag]] - 1
            del self.enemy_unit_tags[unit_tag]
        for unit in self.proxy_units:
            if unit_tag == unit[0]:
                self.proxy_units.remove(unit)
                return
        for unit in self.proxy_buildings:
            if unit_tag == unit[0]:
                self.proxy_buildings.remove(unit)
                return
            
        for queen in self.injecting_queens:
            if unit_tag == queen:
                self.injecting_queens.remove(queen)
                return
        for queen in self.creep_queens:
            if unit_tag == queen:
                self.creep_queens.remove(queen)
                return
        for i in range(0, 6):
            if self.zergling_scout_tags[i] == unit_tag:
                self.zergling_scout_tags[i] = None
                return
        for muta in self.muta_group_tags:
            if unit_tag == muta:
                self.muta_group_tags.remove(muta)
                return
                
        
        if unit_tag in self.mineral_patches.keys():
            drones = list(self.mineral_patches.pop(unit_tag, (None, None, None, None)))
            for drone in self.units.tags_in(drones):
                self.mineral_patches_reversed.pop(drone.tag)
                self.place_drone(drone)
            return
        
        if unit_tag in self.mineral_patches_reversed.keys():
            patch = self.mineral_patches_reversed.pop(unit_tag)[0]
            if self.mineral_patches[patch][1] == unit_tag:
                self.mineral_patches[patch] = (self.mineral_patches[patch][0], self.mineral_patches[patch][2], self.mineral_patches[patch][3], None)
            elif self.mineral_patches[patch][2] == unit_tag:
                self.mineral_patches[patch] = (self.mineral_patches[patch][0], self.mineral_patches[patch][1], self.mineral_patches[patch][3], None)
            elif self.mineral_patches[patch][3] == unit_tag:
                self.mineral_patches[patch] = (self.mineral_patches[patch][0], self.mineral_patches[patch][1], self.mineral_patches[patch][2], None)
            return
        
        if unit_tag in self.extractors.keys():
            drones = list(self.extractors.pop(unit_tag, (None, None, None)))
            for drone in self.units.tags_in(drones):
                self.extractors_reversed.pop(drone.tag)
                self.place_drone(drone)
            return
        
        if unit_tag in self.extractors_reversed.keys():
            patch = self.extractors_reversed.pop(unit_tag)[0]
            if self.extractors[patch][0] == unit_tag:
                self.extractors[patch] = (self.extractors[patch][1], self.extractors[patch][2], None)
            elif self.extractors[patch][1] == unit_tag:
                self.extractors[patch] = (self.extractors[patch][0], self.extractors[patch][2], None)
            elif self.extractors[patch][2] == unit_tag:
                self.extractors[patch] = (self.extractors[patch][0], self.extractors[patch][1], None)
            return


    def convert_location(self, location):
        if self.start_location == Point2((143.5, 32.5)):
            return Point2(location)
        else:
            return Point2((143.5, 32.5)) - Point2(location) + Point2((40.5, 131.5))

    def place_drone(self, drone):
        for mineral_field in [patch for patch in self.mineral_patches.keys() if self.mineral_patches[patch][1] == None]:
            self.mineral_patches[mineral_field] = (self.mineral_patches[mineral_field][0], drone.tag, self.mineral_patches[mineral_field][2], self.mineral_patches[mineral_field][3])
            
            hatch_pos = self.townhalls.closest_to(self.tag_to_unit[mineral_field].position).position
            mineral_pos = self.tag_to_unit[mineral_field].position
            vector = mineral_pos - hatch_pos
            normal_vector = vector / math.sqrt((vector[0] * vector[0]) + (vector[1] * vector[1]))
            drop_off_point = self.townhalls.closest_to(self.tag_to_unit[mineral_field].position).position3d + Point3((normal_vector[0] * 2, normal_vector[1] * 2, 0))
            pick_up_point = self.tag_to_unit[mineral_field].position3d - Point3((normal_vector[0] * .5, normal_vector[1] * .5, 0))
            self.mineral_patches_reversed[drone.tag] = (mineral_field, drop_off_point, pick_up_point)
            return
        for mineral_field in [patch for patch in self.mineral_patches.keys() if self.mineral_patches[patch][2] == None]:
            self.mineral_patches[mineral_field] = (self.mineral_patches[mineral_field][0], self.mineral_patches[mineral_field][1], drone.tag, self.mineral_patches[mineral_field][3])
            
            hatch_pos = self.townhalls.closest_to(self.tag_to_unit[mineral_field].position).position
            mineral_pos = self.tag_to_unit[mineral_field].position
            vector = mineral_pos - hatch_pos
            normal_vector = vector / math.sqrt((vector[0] * vector[0]) + (vector[1] * vector[1]))
            drop_off_point = self.townhalls.closest_to(self.tag_to_unit[mineral_field].position).position3d + Point3((normal_vector[0] * 2, normal_vector[1] * 2, 0))
            pick_up_point = self.tag_to_unit[mineral_field].position3d - Point3((normal_vector[0] * .5, normal_vector[1] * .5, 0))
            self.mineral_patches_reversed[drone.tag] = (mineral_field, drop_off_point, pick_up_point)
            return
        for extractor in [patch for patch in self.extractors.keys() if self.extractors[patch][0] == None]:
            self.extractors[extractor] = (drone.tag, self.extractors[extractor][1], self.extractors[extractor][2])
            
            hatch_pos = self.townhalls.closest_to(self.tag_to_unit[extractor].position).position
            extractor_pos = self.tag_to_unit[extractor].position
            vector = extractor_pos - hatch_pos
            normal_vector = vector / math.sqrt((vector[0] * vector[0]) + (vector[1] * vector[1]))
            drop_off_point = self.townhalls.closest_to(self.tag_to_unit[extractor].position).position3d + Point3((normal_vector[0] * 2, normal_vector[1] * 2, 0))
            pick_up_point = self.tag_to_unit[extractor].position3d - Point3((normal_vector[0] * .5, normal_vector[1] * .5, 0))
            self.extractors_reversed[drone.tag] = (extractor, drop_off_point, pick_up_point)
            return
        for extractor in [patch for patch in self.extractors.keys() if self.extractors[patch][1] == None]:
            self.extractors[extractor] = (self.extractors[extractor][0], drone.tag, self.extractors[extractor][2])
            
            hatch_pos = self.townhalls.closest_to(self.tag_to_unit[extractor].position).position
            extractor_pos = self.tag_to_unit[extractor].position
            vector = extractor_pos - hatch_pos
            normal_vector = vector / math.sqrt((vector[0] * vector[0]) + (vector[1] * vector[1]))
            drop_off_point = self.townhalls.closest_to(self.tag_to_unit[extractor].position).position3d + Point3((normal_vector[0] * 2, normal_vector[1] * 2, 0))
            pick_up_point = self.tag_to_unit[extractor].position3d - Point3((normal_vector[0] * .5, normal_vector[1] * .5, 0))
            self.extractors_reversed[drone.tag] = (extractor, drop_off_point, pick_up_point)
            return
        for extractor in [patch for patch in self.extractors.keys() if self.extractors[patch][2] == None]:
            self.extractors[extractor] = (self.extractors[extractor][0], self.extractors[extractor][1], drone.tag)
            
            hatch_pos = self.townhalls.closest_to(self.tag_to_unit[extractor].position).position
            extractor_pos = self.tag_to_unit[extractor].position
            vector = extractor_pos - hatch_pos
            normal_vector = vector / math.sqrt((vector[0] * vector[0]) + (vector[1] * vector[1]))
            drop_off_point = self.townhalls.closest_to(self.tag_to_unit[extractor].position).position3d + Point3((normal_vector[0] * 2, normal_vector[1] * 2, 0))
            pick_up_point = self.tag_to_unit[extractor].position3d - Point3((normal_vector[0] * .5, normal_vector[1] * .5, 0))
            self.extractors_reversed[drone.tag] = (extractor, drop_off_point, pick_up_point)
            return
        for mineral_field in [patch for patch in self.mineral_patches.keys() if self.mineral_patches[patch][3] == None]:
            self.mineral_patches[mineral_field] = (self.mineral_patches[mineral_field][0], self.mineral_patches[mineral_field][1], self.mineral_patches[mineral_field][2], drone.tag)
            
            hatch_pos = self.townhalls.closest_to(self.tag_to_unit[mineral_field].position).position
            mineral_pos = self.tag_to_unit[mineral_field].position
            vector = mineral_pos - hatch_pos
            normal_vector = vector / math.sqrt((vector[0] * vector[0]) + (vector[1] * vector[1]))
            drop_off_point = self.townhalls.closest_to(self.tag_to_unit[mineral_field].position).position3d + Point3((normal_vector[0] * 2, normal_vector[1] * 2, 0))
            pick_up_point = self.tag_to_unit[mineral_field].position3d - Point3((normal_vector[0] * .5, normal_vector[1] * .5, 0))
            self.mineral_patches_reversed[drone.tag] = (mineral_field, drop_off_point, pick_up_point)
            return
        print("ERROR no place for drone")
    
    def balance_drones(self):
        if round(self.time) > 10 and round(self.time) % 10 == 0:
            for drone in self.units(DRONE).tags_not_in(list(self.mineral_patches_reversed.keys()) + list(self.extractors_reversed.keys()) + [self.builder_drone]):
                self.place_drone(drone)
        
        extra_drones = self.units.tags_in([patch[3] for patch in self.mineral_patches.values() if patch[3] != None])
        missing_drones = len([patch[1] for patch in self.mineral_patches.values() if patch[1] == None])
        missing_drones += len([patch[2] for patch in self.mineral_patches.values() if patch[2] == None])
        missing_drones += len([patch[0] for patch in self.extractors.values() if patch[0] == None])
        missing_drones += len([patch[1] for patch in self.extractors.values() if patch[1] == None])
        missing_drones += len([patch[2] for patch in self.extractors.values() if patch[2] == None])
        for i in range(0, min(missing_drones, len(extra_drones))):
            print("extra drones: " + str(extra_drones))
            print(missing_drones)
            self.remove_drone(extra_drones[i].tag)
            self.place_drone(extra_drones[i])
        
        
    def remove_drone(self, drone_tag):
        if drone_tag in self.mineral_patches_reversed.keys():
            patch = self.mineral_patches_reversed.pop(drone_tag)[0]
            if self.mineral_patches[patch][1] == drone_tag:
                self.mineral_patches[patch] = (self.mineral_patches[patch][0], self.mineral_patches[patch][2], self.mineral_patches[patch][3], None)
            elif self.mineral_patches[patch][2] == drone_tag:
                self.mineral_patches[patch] = (self.mineral_patches[patch][0], self.mineral_patches[patch][1], self.mineral_patches[patch][3], None)
            elif self.mineral_patches[patch][3] == drone_tag:
                self.mineral_patches[patch] = (self.mineral_patches[patch][0], self.mineral_patches[patch][1], self.mineral_patches[patch][2], None)
        elif drone_tag in self.extractors_reversed.keys():
            patch = self.extractors_reversed.pop(drone_tag)[0]
            if self.extractors[patch][0] == drone_tag:
                self.extractors[patch] = (self.extractors[patch][1], self.extractors[patch][2], None)
            elif self.extractors[patch][1] == drone_tag:
                self.extractors[patch] = (self.extractors[patch][0], self.extractors[patch][2], None)
            elif self.extractors[patch][2] == drone_tag:
                self.extractors[patch] = (self.extractors[patch][0], self.extractors[patch][1], None)
    
    def split_drones(self):
        for patch in self.all_units.tags_in(self.mineral_patches.keys()):
            drone = patch.position.closest(self.units(DRONE).tags_not_in(self.mineral_patches_reversed.keys()))
            
            self.mineral_patches[patch.tag] = (self.mineral_patches[patch.tag][0], drone.tag, self.mineral_patches[patch.tag][2], self.mineral_patches[patch.tag][3])
            
            hatch_pos = self.townhalls.closest_to(patch.position).position
            mineral_pos = patch.position
            vector = mineral_pos - hatch_pos
            normal_vector = vector / math.sqrt((vector[0] * vector[0]) + (vector[1] * vector[1]))
            drop_off_point = self.townhalls.closest_to(patch.position).position3d + Point3((normal_vector[0] * 2, normal_vector[1] * 2, 0))
            pick_up_point = patch.position3d - Point3((normal_vector[0] * .5, normal_vector[1] * .5, 0))
            
            self.mineral_patches_reversed[drone.tag] = (patch.tag, drop_off_point, pick_up_point)
        
        for patch in self.all_units.tags_in(self.mineral_patches.keys()):
            if self.mineral_patches[patch.tag][0]:
                drone = patch.position.closest(self.units(DRONE).tags_not_in(self.mineral_patches_reversed.keys()))
                
                self.mineral_patches[patch.tag] = (self.mineral_patches[patch.tag][0], self.mineral_patches[patch.tag][1], drone.tag, self.mineral_patches[patch.tag][3])
                
                hatch_pos = self.townhalls.closest_to(patch.position).position
                mineral_pos = patch.position
                vector = mineral_pos - hatch_pos
                normal_vector = vector / math.sqrt((vector[0] * vector[0]) + (vector[1] * vector[1]))
                drop_off_point = self.townhalls.closest_to(patch.position).position3d + Point3((normal_vector[0] * 2, normal_vector[1] * 2, 0))
                pick_up_point = patch.position3d - Point3((normal_vector[0] * .5, normal_vector[1] * .5, 0))
                
                self.mineral_patches_reversed[drone.tag] = (patch.tag, drop_off_point, pick_up_point)
    
    async def distribute_workers(self, resource_ratio: float = 2):
        for mineral_patch in self.all_units.tags_in(self.mineral_patches.keys()):
            if self.mineral_patches[mineral_patch.tag][1] == None:
                self.client.debug_sphere_out(mineral_patch.position3d, 1, color = Point3((255, 0, 255)))
            elif self.mineral_patches[mineral_patch.tag][2] == None:
                self.client.debug_sphere_out(mineral_patch.position3d, 1, color = Point3((255, 255, 0)))
            elif self.mineral_patches[mineral_patch.tag][3] == None:
                self.client.debug_sphere_out(mineral_patch.position3d, 1, color = Point3((0, 255, 0)))
            else:
                self.client.debug_sphere_out(mineral_patch.position3d, 1, color = Point3((255, 0, 0)))
            
        self.balance_drones()
        
        for drone in self.units.tags_in(self.mineral_patches_reversed.keys()):
            if drone.is_carrying_resource:
                if drone.position.distance_to_closest(self.townhalls) < math.sqrt(10):
                    self.do(drone.return_resource())
                    continue
                if type(drone.order_target) == Point2:
                    if drone.order_target.distance_to(self.mineral_patches_reversed[drone.tag][1].to2) < 1:
                        continue
                    
                mineral_patch = self.tag_to_unit[self.mineral_patches_reversed[drone.tag][0]]
                if mineral_patch != None:
                    drop_off_point = self.mineral_patches_reversed[drone.tag][1]
                    self.do(drone.move(drop_off_point.to2))
                    #self.client.debug_sphere_out(drop_off_point, .5, color = Point3((0, 255, 0)))
                    #self.client.debug_line_out(drone.position3d, drop_off_point, color = Point3((0, 255, 0)))
                else:
                    print("error distribute workers 1")
                
            else:
                mineral_patch = self.tag_to_unit[self.mineral_patches_reversed[drone.tag][0]]
                if mineral_patch != None:
                    if drone.distance_to(mineral_patch) < 2 or drone.position.distance_to_closest(self.units(DRONE).tags_not_in([drone.tag])) < 1.2:
                        if type(drone.order_target) == int:
                            if drone.order_target == mineral_patch.tag:
                                continue
                        self.do(drone.gather(mineral_patch))
                    else:
                        if type(drone.order_target) == Point2:
                            if drone.order_target.distance_to(self.mineral_patches_reversed[drone.tag][2].to2) < 1:
                                continue
                        pick_up_point = self.mineral_patches_reversed[drone.tag][2]
                        self.do(drone.move(pick_up_point.to2))
                        #self.client.debug_sphere_out(pick_up_point, .5, color = Point3((255, 0, 0)))
                        #self.client.debug_line_out(drone.position3d, pick_up_point, color = Point3((255, 0, 0)))
                else:
                    print("error distribute workers 2")
        
        for drone in self.units.tags_in(self.extractors_reversed.keys()):
            if drone.is_carrying_resource:
                if drone.position.distance_to_closest(self.townhalls) < math.sqrt(10):
                    self.do(drone.return_resource())
                    continue
                if type(drone.order_target) == Point2:
                    if drone.order_target.distance_to(self.extractors_reversed[drone.tag][1].to2) < 1:
                        continue
                
                extractor = self.tag_to_unit[self.extractors_reversed[drone.tag][0]]
                if extractor != None:
                    drop_off_point = self.extractors_reversed[drone.tag][1]
                    self.do(drone.move(drop_off_point.to2))
                    #self.client.debug_sphere_out(drop_off_point, .5, color = Point3((0, 255, 0)))
                    #self.client.debug_line_out(drone.position3d, drop_off_point, color = Point3((0, 255, 0)))
                else:
                    print("error distribute workers 3")
                
            else:
                extractor = self.tag_to_unit[self.extractors_reversed[drone.tag][0]]
                if extractor != None:
                    if drone.distance_to(extractor) < 2 or drone.position.distance_to_closest(self.units(DRONE).tags_not_in([drone.tag])) < 1.2:
                        if type(drone.order_target) == int:
                            if drone.order_target == extractor.tag:
                                continue
                        self.do(drone.gather(extractor))
                    else:
                        if type(drone.order_target) == Point2:
                            if drone.order_target.distance_to(self.extractors_reversed[drone.tag][2].to2) < 1:
                                continue
                        pick_up_point = self.extractors_reversed[drone.tag][2]
                        self.do(drone.move(pick_up_point.to2))
                        #self.client.debug_sphere_out(pick_up_point, .5, color = Point3((255, 0, 0)))
                        #self.client.debug_line_out(drone.position3d, pick_up_point, color = Point3((255, 0, 0)))
                else:
                    print("error distribute workers 4")
            
            
        
        
run_game(maps.get("LightshadeLE"), [
        Bot(Race.Zerg, ZergBot()),
        Computer(Race.Terran, Difficulty.VeryHard)
        ], realtime = False)

# Difficulty Easy, Medium, Hard, VeryHard, CheatVision, CheatMoney, CheatInsane

# myunits = Units([], self)
                

# Computer(Race.Terran, Difficulty.VeryHard)































