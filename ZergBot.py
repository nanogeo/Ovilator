
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
from sc2.constants import EGG, DRONE, QUEEN, ZERGLING, BANELING, ROACH, RAVAGER, HYDRALISK, LURKER, MUTALISK, CORRUPTOR, BROODLORD, OVERLORD, OVERSEER, INFESTOR, SWARMHOSTMP, LARVA, VIPER, ULTRALISK, LOCUSTMP, LOCUSTMPFLYING, OVERLORDTRANSPORT
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
from sc2.data import ActionResult

from dijkstra import Graph
from dijkstra import DijkstraSPF
import random
import math
import numpy
from enum import Enum
from dataclasses import dataclass

import Plans
import SpecialActions
import Enums
import States

import matplotlib.pyplot as plt


@dataclass
class ArmyUnitInfo:
    targets: list
    Unit_type: UnitTypeId


class BlankBot(sc2.BotAI):
    def __init__(self):
        self.i = True
    
    async def on_step(self, iteration):
        self.i = False
    

class ZergBot(sc2.BotAI):
    def __init__(self):
        self.unit_command_uses_self_do = True
        self.raw_affects_selection = False
        
        self.debug_message = ""
        self.current_plan = Plans.MacroLingBaneHydra
        self.has_debug = False
        self.debug_interval = 10
        self.unit_command_uses_self_do = True
        self.bases = []
        self.injecting_queens = []
        self.creep_queens = []
        self.inactive_creep_tumors = []
        self.enemy_army_supply = 0
        self.difference_in_bases = 0
        self.saturation = 0
        self.threat_level = 0
        self.build_order = [(0, self.build_drone),
                            (10, self.build_overlord),
                            (14, self.build_drone),
                            (28, self.build_drone),
                            (28, self.build_drone),
                            (30, self.build_drone),
                            (30, self.build_gas),
                            (42, self.build_drone),
                            (43, self.build_pool),
                            (52, self.build_drone),
                            (62, self.build_drone),
                            (62, self.build_hatch)]
        """
        (0, self.build_drone),
                            (10, self.build_overlord),
                            (14, self.build_drone),
                            (28, self.build_drone),
                            (28, self.build_drone),
                            (30, self.build_drone),
                            (30, self.build_gas),
                            (42, self.build_drone),
                            (43, self.build_pool),
                            (52, self.build_drone),
                            (62, self.build_drone),
                            (62, self.build_hatch)
                            
        Pool, Hatch, Gas
        (0, self.build_drone),
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
        (116, self.build_drone)

        
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
        self.unit_production_times = {DRONE: [],	
                                      OVERLORD: [],	
                                      QUEEN: []}
        
        
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
        self.enemy_expos = [0, 0, 0, 0, 0, 0] # nat, line 3, tri 3, line 5, tri 5, mid
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
        self.current_creep_tumor_tags = []
        self.updated_creep = False
        self.creep_queen_state = Enums.QueenState.SPREAD_CREEP
        self.creep_coverage = 0
        self.quad_size_x = 0
        self.quad_size_y = 0
        self.current_quad_x = 0
        self.current_quad_y = 0
        self.quad_status = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.quad_creep_coverage = [[(0, 0), (0, 0), (0, 0), (0, 0)], [(0, 0), (0, 0), (0, 0), (0, 0)], [(0, 0), (0, 0), (0, 0), (0, 0)], [(0, 0), (0, 0), (0, 0), (0, 0)]]
        self.my_pixel_map = []
        self.set_of_non_creep_points = [[set(), set(), set(), set()], [set(), set(), set(), set()], [set(), set(), set(), set()], [set(), set(), set(), set()]]
        self.quad_creep_locations = [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]
        self.overseer_defense = None


        self.unit_ratio = None

        
        
        self.enemy_unit_tags = {}
        self.enemy_unit_numbers = {}
        #self.enemy_army_position = None
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
        self.enemy_army_state = Enums.EnemyArmyState.DEFENDING
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
        self.proxy_status = Enums.ProxyStatus.NONE
        self.proxy_buildings = [] # (tag, type_id, build progress)
        self.proxy_units = [] # (tag, type_id, health)
        self.pulled_worker_tags = []
        self.breaking_proxy = False
        self.proxy_finished_time = 0
        
# army stuff
        self.map_graph = Graph()
        self.army_spot = (127, 81)
        self.attack_position = None
        self.rally_point = None
        self.army_unit_tags = []
        
        self.burrow_researched = False
        self.burrow_movement_researched = False
        self.army_state = Enums.ArmyState.CONSOLIDATING
        self.rally_time = 0

        self.army_condition = Enums.ArmyCondition.DEFENSIVE
        self.army_composition = Enums.ArmyComp.ROACH_HYDRA
        self.army_state_machine = States.ArmyStateMachine(self)
        self.main_army_left = []
        self.main_army_right = []
        self.main_army_left_info = {} # { id : ArmyUnitInfo}
        self.main_army_right_info = {} # { id : ArmyUnitInfo}
        self.army_rally_point_left = None
        self.army_rally_point_right = None
        self.army_target_left = None
        self.army_target_right = None
        self.non_army_units = []
        self.overseer_left = None
        self.overseer_right = None
        self.army_defense_points_left = [(51, 21),
                                        (97, 22),
                                        (106, 39),
                                        (140, 61),
                                        (137, 78)]
        self.army_defense_points_right = [(114, 54),
                                        (124, 62),
                                        (125, 98),
                                        (134, 106),
                                        (146, 133)]
        self.army_consolidation_point_left = (100, 42)
        self.army_consolidation_point_right = (130, 78)
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
        
        self.enemy_main_army_position = None

# special actions
        self.current_ling_runby = None
        self.runby_rally_point = None
        self.runby_attack_point = None
        self.ling_runby_cooldown = 0

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
        self.muta_group_state = Enums.MutaGroupState.CONSOLIDATING
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
        self.swarm_host_state = Enums.SwarmHostState.WAITING
        self.swarm_host_nydus = None
    
    
    async def on_start(self):
        self.client.game_step: int = 2
        self.set_up_map_graph()
        pixel_map = self.game_info.placement_grid
        self.quad_size_x = math.floor(pixel_map.width * .25)
        self.quad_size_y = math.floor(pixel_map.height * .25)
        #self.my_pixel_map = numpy.zeros((pixel_map.width, pixel_map.height))
        if self.army_composition == Enums.ArmyComp.LING_BANE_HYDRA:
            self.unit_ratio = (4, 4, 1)
        if self.army_composition == Enums.ArmyComp.ROACH_HYDRA:
            self.unit_ratio = (2, 1)
        drone_file = open("drone_times.txt", "w")
        drone_file.write("")
        drone_file.close()
        overlord_file = open("overlord_times.txt", "w")
        overlord_file.write("")
        overlord_file.close()
        queen_file = open("queen_times.txt", "w")
        queen_file.write("")
        queen_file.close()


    async def on_step(self, iteration):
        """for i in range(0, 5):
            point = self.army_defense_points_left[i]
            height = self.get_terrain_z_height(Point2(point))
            self._client.debug_sphere_out(Point3((point[0], point[1], height)), 1, color = Point3((255, 0, 0)))
            self._client.debug_text_world(str(i), Point3((point[0], point[1], height)), color = Point3((255, 0, 0)), size = 20)
            point = self.army_defense_points_right[i]
            height = self.get_terrain_z_height(Point2(point))
            self._client.debug_sphere_out(Point3((point[0], point[1], height)), 1, color = Point3((0, 255, 0)))
            self._client.debug_text_world(str(i), Point3((point[0], point[1], height)), color = Point3((0, 255, 0)), size = 20)
        """

        point = self.convert_location(self.army_consolidation_point_left)
        height = self.get_terrain_z_height(Point2(point))
        self._client.debug_sphere_out(Point3((point[0], point[1], height)), 1, color = Point3((255, 0, 0)))
        point = self.convert_location(self.army_consolidation_point_right)
        height = self.get_terrain_z_height(Point2(point))
        self._client.debug_sphere_out(Point3((point[0], point[1], height)), 1, color = Point3((255, 0, 0)))

        self.update_unit_tags()
        if iteration == 1:
            self.split_drones()

        if self.add_new_base != None:
            for mineral_field in self.all_units.mineral_field.closer_than(10, self.tag_to_unit[self.add_new_base].position):
                if mineral_field.is_snapshot:
                    break
                self.mineral_patches[mineral_field.tag] = (mineral_field.mineral_contents == 1800, None, None, None)
                self.add_new_base = None
        await self.distribute_workers()
        await self.execute_build()
        
        await self.inject_larva()
        await self.update_creep(iteration)
        await self.spread_creep()
        await self.position_overlords()
        await self.scouting()
        await self.update_enemy_units()
        await self.track_enemy_army_position()
        if self.build_step >= len(self.build_order):
            await self.test_build_conditions()
            await self.current_plan.execute_plan(self)
            
            await self.scout_with_lings()
            await self.micro()
            await self.create_new_special_actions()
            await self.run_special_actions()

        await self.display_debug_info()
        if len(self.state.chat) > 0:
            for m in self.state.chat:
                if m.message == "Zerglings":
                    await self._client.debug_create_unit([[ZERGLING, 50, self._game_info.map_center, 1]])
                if m.message == "Roaches":
                    await self._client.debug_create_unit([[ROACH, 25, self._game_info.map_center, 1]])
                if m.message == "Hydras":
                    await self._client.debug_create_unit([[HYDRALISK, 25, self._game_info.map_center, 1]])
        
            

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
    
    def make_overseers(self):
        if self.time > 240 and len(self.structures({LAIR, HIVE}).ready) > 0 and len(self.units({OVERSEER, UnitTypeId.OVERLORDCOCOON})) < 3:
            ovi = self.units(OVERLORD).closest_to(self.start_location)
            if self.can_afford(AbilityId.MORPH_OVERSEER):
                self.do(ovi(AbilityId.MORPH_OVERSEER))
                return True
            else:
                return False
        return True

    def add_new_overseer(self, unit_tag):
        if self.overseer_defense == None:
            self.overseer_defense = unit_tag
        elif self.overseer_left == None:
            self.overseer_left = unit_tag
        elif self.overseer_right == None:
            self.overseer_right = unit_tag
        else:
            print("too many overseers")

    def remove_overseer(self, unit_tag):
        if self.overseer_defense == unit_tag:
            self.overseer_defense = None
        elif self.overseer_left == unit_tag:
            self.overseer_left = None
        elif self.overseer_right == unit_tag:
            self.overseer_right = None
        else:
            print("overseer not known")
 
########################################
############### SCOUTING ###############
########################################



    async def scouting(self):
        #send scouts
        if self.scouts_sent == 0 and self.time >= 150:
            if self.enemy_expos[0] == 0:
                #enemy natural is late
                #await self.send_early_scout()
                pass
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

        #respond to scouts
        if self.proxy_location:
            if len(self.enemy_structures) == 0:
                self.proxy_location = None
                self.proxy_status = Enums.ProxyStatus.NONE
            else:
                if self.proxy_location.distance_to_closest(self.enemy_structures) > 10:
                    self.proxy_location = None
                    self.proxy_status = Enums.ProxyStatus.NONE
        if self.time < 240:
            #proxy
            if self.proxy_status == Enums.ProxyStatus.NONE and len(self.enemy_structures) > 0:
                furthest_building = self.enemy_start_locations[0].furthest(self.enemy_structures)
                if self.enemy_start_locations[0].distance_to(furthest_building) > 50:
                    await self.chat_send("Really? A proxy?")
                    self.proxy_location = furthest_building.position
                    self.proxy_status = Enums.ProxyStatus.PR_RAX_STARTED
                    await self.enter_pr_rax_started()
                    await self.gauge_proxy_level()
            elif self.proxy_status != Enums.ProxyStatus.NONE:
                await self.gauge_proxy_level()
                await self.deny_proxy()
   
    
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
            if self.zergling_scout_tags[i] == None or len(self.units.tags_in([self.zergling_scout_tags[i]])) == 0:
                continue
            ling = self.units.tags_in([self.zergling_scout_tags[i]])[0]
            for j in range(0, len(self.scouting_path[i])):
                self.do(ling.move(self.convert_location(Point2(self.scouting_path[i][j])), True))
        return True

    async def send_ling_scout(self, ling, num):
        for i in range(0, len(self.scouting_path[num])):
            self.do(ling.move(self.convert_location(Point2(self.scouting_path[num][i])), True))
    
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
            self.enemy_main_army_position = pos
            for i in range(0, len(self.enemy_expos)):
                if self.enemy_expos[i] > 0:
                    enemy_bases_locations.append(self.convert_location(self.expos[expo_numbers[i]]))
            closest_position = pos.closest(self.army_positions + enemy_bases_locations)
            if closest_position in enemy_bases_locations:
                #enemy is on the defensive
                self.enemy_army_state = Enums.EnemyArmyState.DEFENDING
                self.enemy_attack_point = None
            else:
                if closest_position in [self.army_positions[i] for i in [5, 6, 10, 14, 17]]:
                    self.enemy_army_state = Enums.EnemyArmyState.PREPARING_ATTACK
                else:
                    self.enemy_army_state = Enums.EnemyArmyState.MOVING_TO_ATTACK
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
                self.enemy_attack_point = Point2(self.army_positions[most_likely_path[len(most_likely_path) - 1]])
                
        # 0, 2, 7, 8, 9, 23

    
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
            self.proxy_status = Enums.ProxyStatus.NONE
            await self.chat_send("proxy ended")
        
        if self.enemy_race == Race.Random:
            return

        if self.enemy_race == Race.Terran:
            if self.proxy_status == Enums.ProxyStatus.PR_RAX_STARTED:
                # query build status for barrack
                rax = [building for building in self.proxy_buildings if building[1] == BARRACKS]
                if rax and any([building[2] >= 1 for building in rax]):
                    await self.chat_send("some rax finished")
                    await self.enter_pr_some_rax_finished()
                    self.proxy_status = Enums.ProxyStatus.PR_SOME_RAX_FINISHED
                # query build progress for bunkers
                bunkers = [building for building in self.proxy_buildings if building[1] == BUNKER]
                if bunkers:
                    if not any([unit[1] == MARINE for unit in self.proxy_units]):
                        await self.chat_send("unprotected bunker started")
                        await self.enter_pr_unprotected_bunker()
                        self.proxy_status = Enums.ProxyStatus.PR_UNPROTECTED_BUNKER
                    else:
                        print("protected bunker started")
                        self.proxy_status = Enums.ProxyStatus.PR_PROTECTED_BUNKER
                # attack without bunkers?
                marines = [unit for unit in self.enemy_units if unit.type_id == MARINE]
                if marines and any([unit.position.distance_to_closest(self.townhalls) < 10 for unit in marines]):
                    print("attacking without bunker")
                    self.proxy_status = Enums.ProxyStatus.PR_NO_BUNKER_ATTACK
            elif self.proxy_status == Enums.ProxyStatus.PR_SOME_RAX_FINISHED:
                if not self.breaking_proxy:
                    # query build status for barrack
                    rax = [building for building in self.proxy_buildings if building[1] == BARRACKS]
                    if rax and not any([building[2] < 1 for building in rax]):
                        await self.chat_send("all rax finished")
                        await self.enter_pr_all_rax_finished()
                        self.proxy_status = Enums.ProxyStatus.PR_ALL_RAX_FINISHED
                # query build progress for bunkers
                bunkers = [building for building in self.proxy_buildings if building[1] == BUNKER]
                if bunkers:
                    if not any([unit[1] == MARINE for unit in self.proxy_units]):
                        print("unprotected bunker started")
                        await self.enter_pr_unprotected_bunker()
                        self.proxy_status = Enums.ProxyStatus.PR_UNPROTECTED_BUNKER
                    else:
                        print("protected bunker started")
                        self.proxy_status = Enums.ProxyStatus.PR_PROTECTED_BUNKER
                # attack without bunkers?
                marines = [unit for unit in self.enemy_units if unit.type_id == MARINE]
                if marines and any([unit.position.distance_to_closest(self.townhalls) < 10 for unit in marines]):
                    print("attacking without bunker")
                    self.proxy_status = Enums.ProxyStatus.PR_NO_BUNKER_ATTACK
            elif self.proxy_status == Enums.ProxyStatus.PR_ALL_RAX_FINISHED:
                # query build status for barrack
                rax = [building for building in self.proxy_buildings if building[1] == BARRACKS]
                if rax and any([building[2] < 1 for building in rax]):
                    await self.chat_send("some rax finished")
                    await self.enter_pr_some_rax_finished()
                    self.proxy_status = Enums.ProxyStatus.PR_SOME_RAX_FINISHED
                # query build progress for bunkers
                bunkers = [building for building in self.proxy_buildings if building[1] == BUNKER]
                if bunkers:
                    if not any([unit[1] == MARINE for unit in self.proxy_units]):
                        print("unprotected bunker started")
                        await self.enter_pr_unprotected_bunker()
                        self.proxy_status = Enums.ProxyStatus.PR_UNPROTECTED_BUNKER
                    else:
                        print("protected bunker started")
                        self.proxy_status = Enums.ProxyStatus.PR_PROTECTED_BUNKER
                # attack without bunkers?
                marines = [unit for unit in self.enemy_units if unit.type_id == MARINE]
                if marines and any([unit.position.distance_to_closest(self.townhalls) < 10 for unit in marines]):
                    print("attacking without bunker")
                    self.proxy_status = Enums.ProxyStatus.PR_NO_BUNKER_ATTACK
            elif self.proxy_status == Enums.ProxyStatus.PR_UNPROTECTED_BUNKER:
                # query build progress for bunkers
                if any([unit[1] == MARINE for unit in self.proxy_units]):
                    self.proxy_status = Enums.ProxyStatus.PR_PROTECTED_BUNKER
                elif any([building[1] == BUNKER and building[2] >= 1 for building in self.proxy_buildings]):
                    print("bunker finished")
                    self.proxy_status = Enums.ProxyStatus.PR_BUNKER_FINISHED
            elif self.proxy_status == Enums.ProxyStatus.PR_PROTECTED_BUNKER:
                # query build progress for bunkers
                if any([building[1] == BUNKER and building[2] >= 1 for building in self.proxy_buildings]):
                    print("bunker finished")
                    self.proxy_status = Enums.ProxyStatus.PR_BUNKER_FINISHED
            elif self.proxy_status == Enums.ProxyStatus.PR_NO_BUNKER_ATTACK:
                # query build progress for bunkers
                bunkers = [building for building in self.proxy_buildings if building[1] == BUNKER]
                if bunkers:
                    if not any([unit[1] == MARINE for unit in self.proxy_units]):
                        print("unprotected bunker started")
                        await self.enter_pr_unprotected_bunker()
                        self.proxy_status = Enums.ProxyStatus.PR_UNPROTECTED_BUNKER
                    else:
                        print("protected bunker started")
                        self.proxy_status = Enums.ProxyStatus.PR_PROTECTED_BUNKER
            elif self.proxy_status == Enums.ProxyStatus.PR_BUNKER_FINISHED:
                return
                
    
########################################
################# CREEP ################
########################################

    async def spread_creep(self):
        for tumor in self.structures().tags_in(self.current_creep_tumor_tags):
            if AbilityId.BUILD_CREEPTUMOR_TUMOR in await self.get_available_abilities(tumor):
                spread = False
                for spot in self.creep_spread_to:
                    if tumor.distance_to_squared(spot) < 100:
                        height = self.get_terrain_z_height(spot)
                        self._client.debug_sphere_out(Point3((spot.x, spot.y, height)), .5, color = Point3((0, 255, 0)))
                        self.do(tumor(AbilityId.BUILD_CREEPTUMOR_TUMOR, spot))
                        self.inactive_creep_tumors.append(tumor)
                        self.creep_spread_to.remove(spot)
                        self.current_creep_tumor_tags.remove(tumor.tag)
                        spread = True
                        break
                if not spread:
                    closest_spot = tumor.position.closest(self.creep_spread_to)
                    vector = Point2((closest_spot.x - tumor.position.x, closest_spot.y - tumor.position.y))
                    vector_length = math.sqrt(vector.x * vector.x + vector.y * vector.y)
                    vector = Point2((vector.x / vector_length, vector.y / vector_length))
                    for i in range(8, 1, -1):
                        possible_spot = tumor.position + vector * i
                        height = self.get_terrain_z_height(possible_spot)
                        self._client.debug_sphere_out(Point3((possible_spot.x, possible_spot.y, height)), .5, color = Point3((255, 0, 0)))
                        if (await self._client.query_building_placement(self._game_data.abilities[AbilityId.ZERGBUILD_CREEPTUMOR.value], [Point2(possible_spot)]))[0] == ActionResult.Success:
                            self.do(tumor(AbilityId.BUILD_CREEPTUMOR_TUMOR, possible_spot))
                            self.inactive_creep_tumors.append(tumor)
                            self.creep_spread_to.remove(closest_spot)
                            self.current_creep_tumor_tags.remove(tumor.tag)
                            break
            else:
                break

        if self.creep_queen_state == Enums.QueenState.SPREAD_CREEP:
            await self.place_creep_tumors()
            if self.creep_coverage >= .4 or self.enemy_army_state == Enums.EnemyArmyState.PREPARING_ATTACK:
                self.creep_queen_state = Enums.QueenState.SPREAD_CAREFULLY
                print("creep reached 40%, start saving energy")
            elif self.creep_coverage >= .6 or self.enemy_army_state == Enums.EnemyArmyState.MOVING_TO_ATTACK:
                print("creep reached 60%, stop placing tumors")
                self.creep_queen_state = Enums.QueenState.DEFEND
        elif self.creep_queen_state == Enums.QueenState.SPREAD_CAREFULLY:
            await self.place_creep_tumors_carefully()
            if self.creep_coverage < .4 and self.enemy_army_state == Enums.EnemyArmyState.DEFENDING:
                print("creep receeded to <40%, stop saving energy")
                self.creep_queen_state = Enums.QueenState.SPREAD_CREEP
            elif self.creep_coverage >= .6 or self.enemy_army_state == Enums.EnemyArmyState.MOVING_TO_ATTACK:
                print("creep reached 60%, stop placing tumors")
                self.creep_queen_state = Enums.QueenState.DEFEND
        elif self.creep_queen_state == Enums.QueenState.DEFEND:
            if self.creep_coverage < .6 and not self.enemy_army_state == Enums.EnemyArmyState.MOVING_TO_ATTACK:
                print("creep receeded to <60%, start placing tumors again")
                self.creep_queen_state = Enums.QueenState.SPREAD_CAREFULLY
        
            
    
    async def place_creep_tumors(self):
        for queen in self.creep_queens:
            if self.units.tags_in([queen])[0].energy >= 25 and self.units.tags_in([queen])[0].is_idle and len(self.creep_spread_to) > 0 :
                self.do(self.units.tags_in([queen])[0](AbilityId.BUILD_CREEPTUMOR_QUEEN, Point2(self.creep_spread_to.pop(0))))
                
    async def place_creep_tumors_carefully(self):
        for queen in self.creep_queens:
            if self.units.tags_in([queen])[0].energy >= 75 and self.units.tags_in([queen])[0].is_idle and len(self.creep_spread_to) > 0 :
                self.do(self.units.tags_in([queen])[0](AbilityId.BUILD_CREEPTUMOR_QUEEN, Point2(self.creep_spread_to.pop(0))))
                
    def creep_test_one(self, point):
        return self.start_location.distance_to(point) < 30
    
    def creep_test_one_fail(self):
        return
    
    def creep_test_two(self, point):
        return point.distance_to_closest(self.expansion_locations_list) < 4
    
    def creep_test_two_fail(self):
        return

    def creep_test_three(self, pixel_map, i, j):
        x_quad = int(i / self.quad_size_x)
        y_quad = int(j / self.quad_size_y)
        for k in range(i-1, i+2):
            for l in range(j-1, j+2):
                if k == 0 and l == 0:
                    continue
                if (k, l) in self.set_of_non_creep_points[x_quad][y_quad]:
                    return True
                neighbor_x_quad = x_quad + k - i
                neighbor_y_quad = y_quad + l - j
                if neighbor_x_quad < 0 or neighbor_x_quad >= 4 or neighbor_y_quad < 0 or neighbor_y_quad >= 4:
                    continue
                if (k, l) in self.set_of_non_creep_points[neighbor_x_quad][neighbor_y_quad]:
                    return True

        return False
    
    def creep_test_three_fail(self):
        return

    def creep_test_four(self, point):
        return len(self.enemy_units.exclude_type({DRONE, SCV, PROBE})) and point.distance_to_closest(self.enemy_units.exclude_type({DRONE, SCV, PROBE})) < 10
    
    def creep_test_four_fail(self):
        return
    
    def find_quad_creep_spots(self):
        locations = []
        pixel_map = self.game_info.placement_grid
        for  i in range(self.current_quad_x * self.quad_size_x, (self.current_quad_x + 1) * self.quad_size_x):
            for j in range(self.current_quad_y * self.quad_size_y, (self.current_quad_y + 1) * self.quad_size_y):
                point = Point2((i, j))
                if pixel_map.__getitem__((i, j)) and self.has_creep(point):
                    # find edges of creep
                    if not self.creep_test_three(pixel_map, i, j):
                        self.creep_test_three_fail()
                        continue
                    # ignore any location inside the main
                    if self.creep_test_one(point):
                        self.creep_test_one_fail()
                        continue
                    # ignore any point that would block an expo
                    if self.creep_test_two(point):
                        self.creep_test_two_fail()
                        continue
                    # ignore points close to enemies
                    if self.creep_test_four(point):
                        self.creep_test_four_fail()
                        continue

                    #height = self.get_terrain_z_height(point)
                    #self._client.debug_sphere_out(Point3((i, j, height)), .5, color = Point3((255, 0, 255)))
                    locations.append(point)
        self.quad_creep_locations[self.current_quad_x][self.current_quad_y] = locations
        self.sort_creep_spots()
   
    def sort_creep_spots(self):
        locations = []
        for i in range(0, 4):
            for j in range(0, 4):
                locations.extend(self.quad_creep_locations[i][j])

        current_tumors = self.structures({CREEPTUMOR, CREEPTUMORBURROWED, CREEPTUMORQUEEN})

        if len(self.structures({CREEPTUMOR, CREEPTUMORQUEEN})) > 0:
            locations = sorted(locations, key=lambda point: point.distance_to(self.convert_location(Point2(self.expos[10]))) - 5 * point.distance_to_closest(self.structures({CREEPTUMOR, CREEPTUMORQUEEN})))         
        else:
            locations = sorted(locations, key=lambda point: point.distance_to(self.convert_location(Point2(self.expos[10]))))
        # add all predetermined creep locations to the front
        for pos in self.creep_locations:
            if (len(current_tumors) == 0 or self.convert_location(Point2(pos)).distance_to_closest(current_tumors) > 2) and self.has_creep(self.convert_location(Point2(pos))):
                locations.insert(0, self.convert_location(Point2(pos)))
        
        self.creep_spread_to = locations

    async def update_creep(self, iteration):
        if self.quad_status[self.current_quad_x][self.current_quad_y]:
            await self.update_creep_quadrant()
            self.find_quad_creep_spots()
        elif iteration % 16 == iteration % 160:
            await self.update_creep_quadrant()
            self.find_quad_creep_spots()
        

        self.current_quad_x += 1
        if self.current_quad_x >= 4:
            self.current_quad_x = 0
            self.current_quad_y += 1
            if self.current_quad_y >= 4:
                self.current_quad_y = 0
            

    
    async def update_creep_quadrant(self):
        pixel_map = self.game_info.placement_grid
        self.set_of_non_creep_points[self.current_quad_x][self.current_quad_y] = set()
        valid_points = 0
        points_with_creep = 0
        for i in range(self.current_quad_x * self.quad_size_x, (self.current_quad_x + 1) * self.quad_size_x):
            for j in range(self.current_quad_y * self.quad_size_y, (self.current_quad_y + 1) * self.quad_size_y):
                if pixel_map.__getitem__((i, j)):
                    valid_points += 1
                    if self.has_creep(Point2((i, j))):
                        points_with_creep += 1
                    else:
                        self.set_of_non_creep_points[self.current_quad_x][self.current_quad_y].add((i, j))
        if self.quad_creep_coverage[self.current_quad_x][self.current_quad_y][0] != points_with_creep:
            self.quad_creep_coverage[self.current_quad_x][self.current_quad_y] = (points_with_creep, valid_points)
            self.quad_status[self.current_quad_x][self.current_quad_y] = 1
            await self.update_creep_coverage()
        else:
            self.quad_status[self.current_quad_x][self.current_quad_y] = 0

    async def update_creep_coverage(self):
        valid_points = 0
        points_with_creep = 0
        for i in self.quad_creep_coverage:
            for j in i:
                valid_points += j[1]
                points_with_creep += j[0]
        self.creep_coverage = points_with_creep / valid_points


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
        await self.micro_overseers()
        self.army_state_machine.run_state_machine()

        need_to_protect = None
        # are we being attacked right now?
        for enemy in self.enemy_units.exclude_type([DRONE, PROBE, SCV]):
            for hatch in self.townhalls:
                if enemy.distance_to(hatch) < 20:
                    need_to_protect = enemy.position
                    break
            if need_to_protect == None and len(self.main_army_left + self.main_army_right) > 0:
                if enemy.position.distance_to_closest(self.units.tags_in(self.main_army_left + self.main_army_right)) < 5:
                    need_to_protect = enemy.position
                    break
            else:
                break
        if self.creep_queen_state == Enums.QueenState.DEFEND:
            await self.micro_queen_defense(need_to_protect)
        if self.army_composition == Enums.ArmyComp.LING_BANE_HYDRA or self.army_composition == Enums.ArmyComp.LING_BANE_MUTA:
            await self.micro_banes()
        if self.army_composition == Enums.ArmyComp.LING_BANE_MUTA:
            await self.micro_mutas()
        if self.army_composition == Enums.ArmyComp.ROACH_SWARM_HOST:
            await self.spawn_nydus_worm()
            await self.micro_swarm_hosts()
            await self.micro_locusts()
        if len(self.units(INFESTOR)) > 0:
            await self.micro_infestors()
        """
        if self.army_state == Enums.ArmyState.CONSOLIDATING:
            if self.enemy_army_state == Enums.EnemyArmyState.MOVING_TO_ATTACK or self.enemy_army_state == Enums.EnemyArmyState.PREPARING_ATTACK:
                # move to flank positions
                possible_attack_points = [23, 9, 8, 0, 2]
                for i in range(0, len(possible_attack_points)):
                    if self.enemy_attack_point == self.army_positions[possible_attack_points[i]]:
                        for unit in self.units.tags_in(self.main_army_left):
                            if unit.distance_to_squared(self.convert_location(self.army_defense_points_left[i])) > 25:
                                self.do(unit.move(self.convert_location(self.army_defense_points_left[i])))
                        for unit in self.units.tags_in(self.main_army_right):
                            if unit.distance_to_squared(self.convert_location(self.army_defense_points_right[i])) > 25:
                                self.do(unit.move(self.convert_location(self.army_defense_points_right[i])))
            else:
                # move to consolidation points
                for unit in self.units.tags_in(self.main_army_left):
                    if unit.distance_to_squared(self.convert_location(self.army_consolidation_point_left)) > 25:
                        self.do(unit.move(self.convert_location(self.army_consolidation_point_left)))
                for unit in self.units.tags_in(self.main_army_right):
                    if unit.distance_to_squared(self.convert_location(self.army_consolidation_point_right)) > 25:
                        self.do(unit.move(self.convert_location(self.army_consolidation_point_right)))

            if need_to_protect:
                self.army_state = Enums.ArmyState.PROTECTING
                for unit in self.units.tags_in(self.main_army_left + self.main_army_right + self.creep_queens):
                    self.do(unit.attack(need_to_protect))
            # if we have more than 90 army supply ready then go to the rally point
            if sum(self.calculate_supply_cost(unit.type_id) for unit in self.units.tags_in(self.main_army_left + self.main_army_right)) >= 90:
                self.army_state = Enums.ArmyState.RALLYING
                self.rally_time = self.time
                await self.find_attack_and_rally_points()
                for unit in self.units.tags_in(self.main_army_left):
                    self.do(unit.attack(Point2(self.army_rally_point_left)))
                for unit in self.units.tags_in(self.main_army_right):
                    self.do(unit.attack(Point2(self.army_rally_point_right)))
        elif self.army_state == Enums.ArmyState.RALLYING:
            # if we're attacked while we're launching an attack then go back to defend
            # TODO determine if we need to defend and how much with
            if need_to_protect:
                self.army_state = Enums.ArmyState.PROTECTING
                for unit in self.units.tags_in(self.main_army_left + self.main_army_right + self.creep_queens):
                    self.do(unit.attack(need_to_protect))
            # if we've been rallying for a while just attack
            print("rally time " + str(self.rally_time + 20))
            if (self.rally_time + 20) < self.time:
                self.army_state = Enums.ArmyState.ATTACKING
                left_targets = self.get_targets_left()
                for unit_tag, info in self.main_army_left_info:
                    info[0] = left_targets
                right_targets = self.get_targets_right()
                for unit_tag, info in self.main_army_right_info:
                    info[0] = right_targets
                    return
            # is everyone in position?
            for unit in self.units.tags_in(self.main_army_left):
                if unit.distance_to(Point2(self.army_rally_point_left)) > 10:
                    # unit is not yet at the rally point
                    print("waiting on " + str(unit.type_id))
                    self.do(unit.attack(self.army_rally_point_left))
                    self._client.debug_sphere_out(Point3((unit.position3d[0], unit.position3d[1], unit.position3d[2])), 1, color = Point3((0, 255, 0)))
                    return
            for unit in self.units.tags_in(self.main_army_right):
                if unit.distance_to(Point2(self.army_rally_point_right)) > 10:
                    # unit is not yet at the rally point
                    print("waiting on " + str(unit.type_id))
                    self.do(unit.attack(self.army_rally_point_right))
                    self._client.debug_sphere_out(Point3((unit.position3d[0], unit.position3d[1], unit.position3d[2])), 1, color = Point3((0, 255, 0)))
                    return
            # everyone is at the rally point then update targets list
            self.army_state = Enums.ArmyState.ATTACKING
            left_targets = self.get_targets_left()
            for unit_tag, info in self.main_army_left_info:
                info[0] = left_targets
            right_targets = self.get_targets_right()
            for unit_tag, info in self.main_army_right_info:
                info[0] = right_targets
        elif self.army_state == Enums.ArmyState.ATTACKING:
            avg_dist_left = self.median_center(self.units.tags_in(self.main_army_left)).distance_to(self.army_target_left)
            for unit in self.units.tags_in(self.main_army_left):
                if unit.position.distance_to(self.army_target_left) > avg_dist_left:
                    self._client.debug_sphere_out(unit.position3d, 1, color = Point3((255, 255, 0)))
            enemy_supply = 0
            # determine enemy army supply
            for tag in self.enemy_unit_tags.keys():
                if self.enemy_unit_tags[tag] not in [PROBE, DRONE, SCV]:
                    enemy_supply += self.calculate_supply_cost(self.enemy_unit_tags[tag])
            # if we have 2x more army supply then flood new units
            if self.supply_army > enemy_supply * 2:
                for unit in self.units.tags_in(self.main_army_left).idle:
                    self.do(unit.attack(Point2(self.army_target_left)))
                    self.do(unit.attack(Point2(self.enemy_start_locations[0]), queue = True))
                for unit in self.units.tags_in(self.main_army_right).idle:
                    self.do(unit.attack(Point2(self.army_target_right)))
                    self.do(unit.attack(Point2(self.enemy_start_locations[0]), queue = True))
            # if the attack has been killed off go back to consolidating
            if len(self.units.tags_in(self.main_army_left + self.main_army_right)) == 0:
                print("consolidate")
                self.army_state = Enums.ArmyState.CONSOLIDATING
            for roach in self.units({ROACH, ROACHBURROWED}).tags_in(self.army_unit_tags):
                await self.micro_roach(roach)
        elif self.army_state == Enums.ArmyState.PROTECTING:
            # if the attack has been dealt with go back to consolidating
            if need_to_protect == None:
                self.army_state = Enums.ArmyState.CONSOLIDATING
        """

    def need_to_protect(self):
        need_to_protect = None
        # are we being attacked right now?
        for enemy in self.enemy_units.exclude_type([DRONE, PROBE, SCV]):
            for hatch in self.townhalls:
                if enemy.distance_to(hatch) < 20:
                    need_to_protect = enemy.position
                    break
            if need_to_protect == None and len(self.main_army_left + self.main_army_right) > 0:
                if enemy.position.distance_to_closest(self.units.tags_in(self.main_army_left + self.main_army_right)) < 5:
                    need_to_protect = enemy.position
                    break
            else:
                break
        return need_to_protect

    def get_consolidation_points(self):
        return (self.convert_location(self.army_consolidation_point_left), self.convert_location(self.army_consolidation_point_right))

    def get_flank_points(self):
        possible_attack_points = [23, 9, 8, 0, 2]
        for i in range(0, len(possible_attack_points)):
            if self.enemy_attack_point == self.army_positions[possible_attack_points[i]]:
                return (self.convert_location(self.army_defense_points_left[i]), self.convert_location(self.army_defense_points_right[i]))

    def move_units(self, units, position):
        for unit in units:
            if unit.distance_to(position) > 10:
                self.do(unit.move(position))

    def move_army_to_next_point(self):
        for unit_tag, info in self.main_army_left_info.items():
            unit = self.tag_to_unit.get(unit_tag)
            if unit and unit.distance_to(info.targets[0]) > 10:
                self.do(unit.move(info.targets[0]))
        for unit_tag, info in self.main_army_right_info.items():
            unit = self.tag_to_unit.get(unit_tag)
            if unit and unit.distance_to(info.targets[0]) > 10:
                self.do(unit.move(info.targets[0]))
    
    def all_units_at_target(self):
        for unit_tag, info in self.main_army_left_info.items():
            unit = self.tag_to_unit.get(unit_tag)
            if unit and unit.distance_to(info.targets[0]) > 10:
                return False
        for unit_tag, info in self.main_army_right_info.items():
            unit = self.tag_to_unit.get(unit_tag)
            if unit and unit.distance_to(info.targets[0]) > 10:
                return False
        return True

    def update_targets(self):
        for unit_tag, info in self.main_army_left_info.items():
            unit = self.tag_to_unit.get(unit_tag)
            if unit and len(info.targets) > 1 and unit.distance_to(info.targets[0]) < 10:
                info.targets.pop(0)
        for unit_tag, info in self.main_army_right_info.items():
            unit = self.tag_to_unit.get(unit_tag)
            if unit and len(info.targets) > 1 and unit.distance_to(info.targets[0]) < 10:
                info.targets.pop(0)

    def army_attack_next_point(self):
        left_median = self.median_center(self.units.tags_in(self.main_army_left))
        height = self.get_terrain_z_height(left_median)
        self._client.debug_sphere_out(Point3((left_median[0], left_median[1], height)), 1, color = Point3((255, 0, 0)))
        for unit_tag, info in self.main_army_left_info.items():
            # TODO if it is not a spell caster
            unit = self.tag_to_unit.get(unit_tag)
            if unit and unit.distance_to(info.targets[0]) + 1 > left_median.distance_to(info.targets[0]) and unit.weapon_cooldown > 0:
                self._client.debug_sphere_out(unit.position3d, 1, color = Point3((0, 255, 0)))
                self.do(unit.move(info.targets[0]))
            elif unit:
                self.do(unit.attack(info.targets[0]))
        right_median = self.median_center(self.units.tags_in(self.main_army_right))
        height = self.get_terrain_z_height(right_median)
        self._client.debug_sphere_out(Point3((right_median[0], right_median[1], height)), 1, color = Point3((255, 0, 0))) 
        for unit_tag, info in self.main_army_right_info.items():
            # TODO if it is not a spell caster
            unit = self.tag_to_unit.get(unit_tag)
            if unit and unit.distance_to(info.targets[0]) + 1 > left_median.distance_to(info.targets[0]) and unit.weapon_cooldown > 0:
                self.do(unit.move(info.targets[0]))
                self._client.debug_sphere_out(unit.position3d, 1, color = Point3((0, 255, 0)))
            elif unit:
                self.do(unit.attack(info.targets[0]))

        
    
    async def position_army_defensive(self):
        if self.enemy_army_state == Enums.EnemyArmyState.MOVING_TO_ATTACK:
            flank_pos = self.find_flanking_position(self.enemy_attack_point)
        

    def find_flanking_position(self):
        pass

    
    def get_targets_right(self):
        targets = []
        if self.enemy_expos[4] == 1:
            # triangle 5th
            targets.append(self.convert_location(self.rally_points[0]))
            targets.append(self.convert_location(self.expos[2]))
            targets.append(self.convert_location(self.expos[9]))
            targets.append(self.convert_location(self.expos[7]))
            targets.append(self.enemy_start_locations[0])
        elif self.enemy_expos[2] == 1:
            # triangle 3rd
            targets.append(self.convert_location(self.rally_points[6]))
            targets.append(self.convert_location(self.expos[9]))
            targets.append(self.convert_location(self.expos[7]))
            targets.append(self.enemy_start_locations[0])
        else:
            # nat
            targets.append(self.convert_location(self.rally_points[1]))
            targets.append(self.convert_location(self.expos[7]))
            targets.append(self.enemy_start_locations[0])
        return targets

    def get_targets_left(self):
        targets = []
        if self.enemy_expos[3] == 1:
            # inline 5th
            targets.append(self.convert_location(self.rally_points[5]))
            targets.append(self.convert_location(self.expos[6]))
            targets.append(self.convert_location(self.expos[3]))
            targets.append(self.convert_location(self.expos[7]))
            targets.append(self.enemy_start_locations[0])
        elif self.enemy_expos[1] == 1:
            # inline 3rd
            targets.append(self.convert_location(self.rally_points[5]))
            targets.append(self.convert_location(self.expos[3]))
            targets.append(self.convert_location(self.expos[7]))
            targets.append(self.enemy_start_locations[0])
        else:
            # nat
            targets.append(self.convert_location(self.rally_points[2]))
            targets.append(self.convert_location(self.expos[7]))
            targets.append(self.enemy_start_locations[0])
        return targets

    async def find_attack_and_rally_points(self):
        # for left hand army
        if self.enemy_expos[3] == 1:
            # inline 5th
            self.army_rally_point_left = self.convert_location(self.rally_points[5])
            self.army_target_left = self.convert_location(self.expos[6])
        elif self.enemy_expos[1] == 1:
            # inline 3rd
            self.army_rally_point_left = self.convert_location(self.rally_points[5])
            self.army_target_left = self.convert_location(self.expos[3])
        else:
            # natural
            self.army_rally_point_left = self.convert_location(self.rally_points[2])
            self.army_target_left = self.convert_location(self.expos[7])

        # for right hand army
        if self.enemy_expos[4] == 1:
            # triangle 5th
            self.army_rally_point_right = self.convert_location(self.rally_points[0])
            self.army_target_right = self.convert_location(self.expos[2])
        elif self.enemy_expos[2] == 1:
            # triangle 3rd
            self.army_rally_point_right = self.convert_location(self.rally_points[6])
            self.army_target_right = self.convert_location(self.expos[9])
        else:
            # natural
            self.army_rally_point_right = self.convert_location(self.rally_points[1])
            self.army_target_right = self.convert_location(self.expos[7])
        
            
    async def micro_queen_defense(self, need_to_protect):
        if self.enemy_attack_point == None:
            newest_base = min(self.bases, key = lambda u: u.age)
        else:
            newest_base = self.enemy_attack_point.closest(self.townhalls)
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
                
    async def micro_overseers(self):
        if len(self.units.tags_in(self.creep_queens)) > 0 and self.overseer_defense != None:
            center = self.median_center(self.units.tags_in(self.creep_queens))
            for unit in self.units.tags_in([self.overseer_defense]):
                if unit.distance_to(center) > 2:
                    self.do(unit.move(center))
        if len(self.units.tags_in(self.main_army_left)) > 0 and self.overseer_left != None:
            center = self.median_center(self.units.tags_in(self.main_army_left))
            for unit in self.units.tags_in([self.overseer_left]):
                if unit.distance_to(center) > 2:
                    self.do(unit.move(center))
        if len(self.units.tags_in(self.main_army_right)) > 0 and self.overseer_right != None:
            center = self.median_center(self.units.tags_in(self.main_army_right))
            for unit in self.units.tags_in([self.overseer_right]):
                if unit.distance_to(center) > 2:
                    self.do(unit.move(center))


    async def micro_roach(self, roach):
        if roach.health_percentage < .7 and self.burrow_researched and self.burrow_movement_researched and not roach.is_burrowed:
            self.do(roach(AbilityId.BURROWDOWN_ROACH))
        elif roach.is_burrowed and roach.health_percentage > .9:
            self.do(roach(AbilityId.BURROWUP_ROACH))
        elif roach.is_burrowed:
            self.do(roach.move(Point2(self.rally_point)))
            
    async def micro_mutas(self):
        if len(self.muta_group_tags) == 0:
            self.muta_group_state = Enums.MutaGroupState.CONSOLIDATING
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
        if self.muta_group_state == Enums.MutaGroupState.CONSOLIDATING:
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
                    self.muta_group_state = Enums.MutaGroupState.MOVING_TO_RALLY
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
        elif self.muta_group_state == Enums.MutaGroupState.MOVING_TO_RALLY:
            if center.distance_to(self.muta_rally_point_attack) < 2:
                if self.muta_attack_point:
                    self.muta_group_state = Enums.MutaGroupState.MOVING_TO_ATTACK
                    for muta in muta_group:
                        self.do(muta.move(self.muta_attack_point))
                else:
                    self.muta_group_state = Enums.MutaGroupState.RETREATING
                    for muta in muta_group:
                        self.do(muta.move(Point2(self.army_spot)))
        elif self.muta_group_state == Enums.MutaGroupState.MOVING_TO_ATTACK:
            if center.distance_to(self.muta_attack_point) < 2:
                self.muta_group_state = Enums.MutaGroupState.ATTACKING
        elif self.muta_group_state == Enums.MutaGroupState.ATTACKING:
            # when the workers get away, move on
            if len(self.enemy_units({SCV, PROBE, DRONE})) == 0 or self.muta_attack_point.distance_to_closest(self.enemy_units({SCV, PROBE, DRONE})) > 6:
                # TODO if mutas are hurt, retreat them to heal up
                self.find_muta_rally_and_attack_points()
                for muta in muta_group:
                    self.do(muta.move(self.muta_rally_point_attack))
                self.muta_group_state = Enums.MutaGroupState.MOVING_TO_RALLY
            else:
                # attack workers
                for muta in muta_group:
                    self.do(muta.attack(self.enemy_units({SCV, PROBE, DRONE}).closest_to(self.muta_attack_point)))
        elif self.muta_group_state == Enums.MutaGroupState.RETREATING:
            if center.distance_to(Point2(self.army_spot)) < 2:
                # TODO add new mutas to group
                self.muta_group_state = Enums.MutaGroupState.CONSOLIDATING

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
        if self.swarm_host_state == Enums.SwarmHostState.WAITING:
            if self.time - self.last_locust_wave > 43 and len(self.structures(NYDUSNETWORK)[0].passengers) >= 10 and len(self.structures(NYDUSCANAL).ready) > 0:
                self.swarm_host_state = Enums.SwarmHostState.UNLOADING
                nydus = self.structures(NYDUSCANAL).ready.random
                self.do(nydus(AbilityId.UNLOADALL_NYDUSWORM))
                self.swarm_host_nydus = nydus.tag
        elif self.swarm_host_state == Enums.SwarmHostState.UNLOADING:
            nydus = self.structures.tags_in([self.swarm_host_nydus])[0]
            target = nydus.position.closest(self.enemy_structures({NEXUS, HATCHERY, LAIR, HIVE, COMMANDCENTER, ORBITALCOMMAND, PLANETARYFORTRESS}))
            if not self.structures(NYDUSNETWORK)[0].has_cargo:
                for swarm_host in self.units(SWARMHOSTMP):
                    self.do(swarm_host(AbilityId.EFFECT_SPAWNLOCUSTS, target.position))
                    self.do(swarm_host.smart(nydus, True))
                self.swarm_host_state = Enums.SwarmHostState.WAITING
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
        if self.army_state == Enums.ArmyState.ATTACKING or self.army_state == Enums.ArmyState.PROTECTING:
            if len(self.units(BANELING)) > 0 and len(self.enemy_units(MARINE)) > 0:
                for baneling in self.units(BANELING):
                    if len(self.enemy_units(MARINE).closer_than(2, baneling.position)) >= 4:
                        self.do(baneling(AbilityId.EXPLODE_EXPLODE))
    
    async def micro_infestors(self):
        print("have infestors")
        if self.army_state == Enums.ArmyState.ATTACKING or self.army_state == Enums.ArmyState.PROTECTING:
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
            if self.proxy_status == Enums.ProxyStatus.PR_RAX_STARTED:
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
                     
            elif self.proxy_status == Enums.ProxyStatus.PR_SOME_RAX_FINISHED:
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
                        break
                    if drone.health >= 40:
                        self.pulled_worker_tags.append(drone.tag)
                
                for ling in self.units(ZERGLING).ready:
                    if ling.distance_to(self.proxy_location) > 10:
                        self.do(ling.move(self.units.tags_in(self.pulled_worker_tags).center))
                    else:
                        await self.micro_vs_proxy(ling)
                for drone in self.units.tags_in(self.pulled_worker_tags):
                    await self.micro_vs_proxy(drone)
                
            elif self.proxy_status == Enums.ProxyStatus.PR_ALL_RAX_FINISHED:
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
                        break
                    if drone.health >= 40:
                        self.pulled_worker_tags.append(drone.tag)
                
                for ling in self.units(ZERGLING).ready:
                    if ling.distance_to(self.proxy_location) > 10:
                        self.do(ling.move(self.units.tags_in(self.pulled_worker_tags).center))
                    else:
                        await self.micro_vs_proxy(ling)
                for drone in self.units.tags_in(self.pulled_worker_tags):
                    await self.micro_vs_proxy(drone)
                
            """elif self.proxy_status == Enums.ProxyStatus.PR_UNPROTECTED_BUNKER:
                
            elif self.proxy_status == Enums.ProxyStatus.PR_PROTECTED_BUNKER:
                
            elif self.proxy_status == Enums.ProxyStatus.PR_NO_BUNKER_ATTACK:
                
            elif self.proxy_status == Enums.ProxyStatus.PR_BUNKER_FINISHED:"""
                
            
    
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

    async def build_building(self, building):
        if self.builder_drone == None or not self.builder_drone in self.tag_to_unit.keys():
            self.build_location = None
            self.builder_drone = self.select_build_worker(self.start_location).tag
            self.remove_drone(self.builder_drone)
            if not self.builder_drone in self.tag_to_unit.keys():
                self.builder_drone = None
                self.add_debug_info("no builder drone")
                return False
        if self.build_location == None:
            self.build_location = await self.find_placement(HATCHERY, near = self.start_location, max_distance = 30)
            if self.build_location != None and not await self.can_place_single(building, self.build_location):
                self.build_location = None
                self.add_debug_info("no build location")
                return False
        #if AbilityId.HARVEST_GATHER in self.tag_to_unit[self.builder_drone].orders:
        if self.build_location != None:
            builder = self.tag_to_unit[self.builder_drone]
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.build(building, self.build_location))
            self.add_debug_info("build " + str(building))

    async def build_gas(self):
        print("build gas??")
        if self.minerals >= 25:
            print("build gas")
            for hatch in self.structures({HATCHERY, LAIR, HIVE}).ready:
                vespenes = self.vespene_geyser.closer_than(10.0, hatch)
                for vespene in vespenes:
                    worker = self.select_build_worker(vespene.position)
                    if worker is None:
                        break
                    self.remove_drone(worker.tag)
                    self._client.debug_sphere_out(Point3((vespene.position[0], vespene.position[1], self.get_terrain_z_height(vespene.position))), 1, color = Point3((255, 255, 0)))
                    self.do(worker.build(EXTRACTOR, vespene))
                    return True
        return False
    
    def make_baneling(self):
        lings = self.units(ZERGLING).tags_in(self.main_army_left + self.main_army_right)
        if len(lings) > 0:
            self.do(lings[0](AbilityId.MORPHZERGLINGTOBANELING_BANELING))

    def make_dropperlord(self):
        overlord = self.start_location.closest(self.units(OVERLORD).ready)
        if self.can_afford(AbilityId.MORPH_OVERLORDTRANSPORT):
            self.do(overlord(AbilityId.MORPH_OVERLORDTRANSPORT))

    async def build_extractor(self):
        """
        if self.vespene > 500 or (self.time < 360 and len(self.structures(EXTRACTOR)) >= 2):
            return"""
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
    
    def get_upgrade(self, building_type, upgrade, upgrade_ability):
        if len(self.structures(building_type).ready.idle) > 0 and self.can_afford(upgrade):
            building = self.structures(building_type).ready.idle.random
            self.do(building(upgrade_ability))
            return True
        else:
            return False


    async def build_spores(self):
        for spore_pos in self.spore_positions:
            pos = self.convert_location(spore_pos)
            if self.minerals > 150 and pos.distance_to_closest(self.townhalls.ready) < 10 and self.has_creep(pos):
                if len(self.structures(SPORECRAWLER)) == 0 or pos.distance_to_closest(self.structures(SPORECRAWLER)) > 2:
                    drone = pos.closest(self.units(DRONE))
                    self.remove_drone(drone.tag)
                    self.do(drone.build(SPORECRAWLER, pos))


########################################
############ SPECIAL ACTIONS ###########
########################################

    async def run_special_actions(self):
        if self.current_ling_runby:
            if self.current_ling_runby.check_cancel_conditions():
                # return units etc
                self.ling_runby_cooldown = self.current_ling_runby.cooldown
                self.current_ling_runby = None
                print("delete ling runby")
            else:
                await self.current_ling_runby.run_action()
        else:
            self.ling_runby_cooldown -= self.step_time[3]


    async def create_new_special_actions(self):
        if self.ling_runby_cooldown <= 0 and self.current_ling_runby == None and SpecialActions.LingRunby.check_prereqs(self):
            self.find_runby_location()
            lings = (self.units(ZERGLING).tags_in(self.main_army_left + self.main_army_right).closest_n_units(self.runby_rally_point, 10)).tags
            for tag in lings:
                if tag in self.main_army_left:
                    self.main_army_left.remove(tag)
                elif tag in self.main_army_right:
                    self.main_army_right.remove(tag)
            self.current_ling_runby = SpecialActions.LingRunby(self, lings, self.runby_attack_point, self.runby_rally_point)
            print(self.current_ling_runby)
        
    def find_runby_location(self):
        left_rally = self.convert_location((55, 23))
        right_rally = self.convert_location((129, 141))
        print("RUNBY")
        if self.enemy_main_army_position == None or self.enemy_main_army_position.distance_to(left_rally) < self.enemy_main_army_position.distance_to(right_rally):
            self.runby_rally_point = left_rally
            attack_point = 7
            if self.enemy_expos[3]:
                attack_point = 6
            elif self.enemy_expos[1]:
                attack_point = 3
            print("LEFT")
        else:
            self.runby_rally_point = right_rally
            attack_point = 7
            if self.enemy_expos[4]:
                attack_point =  2
            elif self.enemy_expos[2]:
                attack_point = 9
            print("RIGHT")
        self.runby_attack_point = self.convert_location(self.expos[attack_point])
        # nat, line 3, tri 3, line 5, tri 5, mid 7, 3, 9, 6, 2, 4
            



########################################
################ UTILITY ###############
########################################
    
    def add_debug_info(self, info):
        self.debug_message += info + "\n"

    async def display_debug_info(self):
        self.add_debug_info("Army State: " + self.army_state_machine.get_state())
        self.add_debug_info(str(self.enemy_unit_numbers))
        self.add_debug_info("enemy bases "  + str(sum(self.enemy_expos) + 1) + " my bases " + str(len(self.townhalls)))
        self.add_debug_info("next expo: " + str(self.last_expansion_time + 120))
        self.add_debug_info(self.creep_queen_state.name)
        self.add_debug_info(self.enemy_army_state.name)
        if self.proxy_status != Enums.ProxyStatus.NONE:
            self.add_debug_info(self.proxy_units)
            self.add_debug_info(self.proxy_buildings)
        

        self._client.debug_text_screen(self.debug_message, (.1, .1), Point3((255, 0, 0)), 20)
        self.debug_message = self.current_plan.to_string() + "\n"
        for i in range(3, -1, -1):
            for j in range(0, 4):
                if self.quad_status[i][j] == 0:
                    self._client.debug_text_screen("\n"*(3-j) + " "*i + '0', (.3, .1), Point3((255, 0, 0)), 20)
                else:
                    self._client.debug_text_screen("\n"*(3-j) + " "*i + '1', (.3, .1), Point3((0, 255, 0)), 20)

    def set_up_map_graph(self):
        for index, point in enumerate(self.army_positions):
            self.army_positions[index] = self.convert_location(point)
        for i in range(0, len(self.army_position_links)):
            for j in range(0, len(self.army_position_links[i])):
                self.map_graph.add_edge(i, self.army_position_links[i][j], Point2(self.army_positions[i]).distance_to(Point2(self.army_positions[self.army_position_links[i][j]])))

    def median_center(self, units):
        guess = units.center
        done = False
        tests = [Point2((0, 1)), Point2((1, 0)), Point2((-1, 0)), Point2((0, -1))]
        dist = sum(unit.position.distance_to(guess) for unit in units)

        while not done:
            done = True
            for test in tests:
                new_guess = guess + test
                new_dist = sum(unit.position.distance_to(new_guess) for unit in units)
                if new_dist < dist:
                    guess = new_guess
                    dist = new_dist
                    done = False
                    break
            if done:
                break
        return guess
    

    async def test_build_conditions(self):
        self.update_plan_conditions()
        best_value = 0
        best_plan = self.current_plan
        for build in Plans.all_builds:
            value = build.test_conditions(self)
            if value > best_value:
                best_value = value
                best_plan = build
        if self.current_plan != best_plan:
            self.current_plan = best_plan

    def update_plan_conditions(self):
        self.enemy_army_supply = self.update_enemy_army_supply()
        self.difference_in_bases = self.update_difference_in_bases()
        self.saturation = self.update_saturation()
        self.threat_level = self.update_threat_level()


    def get_army_comp(self):
        return self.army_composition

    def update_enemy_army_supply(self):
        supply = 0
        for tag in self.enemy_unit_tags.keys():
            if self.enemy_unit_tags[tag] not in [PROBE, DRONE, SCV]:
                supply += self.calculate_supply_cost(self.enemy_unit_tags[tag])
        return supply
    
    def update_difference_in_bases(self):
        return (len(self.townhalls) + self.already_pending(HATCHERY)) - (sum(self.enemy_expos) + 1)

    def update_saturation(self):
        drone_max = ((len(self.townhalls) + self.already_pending(HATCHERY)) * 16) + (len(self.structures(EXTRACTOR)) * 3)
        return self.supply_workers / drone_max

    def update_threat_level(self):
        if self.supply_army == 0:
            return math.inf
        threat = self.enemy_army_supply / (self.supply_army - (len(self.creep_queens) * 2))
        if self.enemy_army_state == Enums.EnemyArmyState.DEFENDING:
            threat *= .5
        elif self.enemy_army_state == Enums.EnemyArmyState.PREPARING_ATTACK:
            threat *= .8
        elif self.enemy_army_state == Enums.EnemyArmyState.MOVING_TO_ATTACK:
            threat *= 1.5
        return threat

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
        elif unit.type_id == ZERGLING and len(self.units.tags_in(self.zergling_scout_tags)) < 6:
            for i in range(0, len(self.zergling_scout_tags)):
                if self.zergling_scout_tags[i] == None:
                    self.zergling_scout_tags[i] = unit.tag
                    await self.send_ling_scout(unit, i)
                    break
        elif unit.type_id == SWARMHOSTMP:
            self.do(unit.smart(self.structures(NYDUSNETWORK)[0]))
        elif unit.type_id == DRONE:
            self.place_drone(unit)
        elif unit.type_id == OVERSEER:
            self.add_new_overseer(unit.tag)
        elif unit.type_id not in [LARVA, EGG, DRONE, QUEEN, OVERLORD, OVERSEER, OVERLORDTRANSPORT, MUTALISK, SWARMHOSTMP]:
            # TODO make this better
            if len(self.main_army_left) < len(self.main_army_right):
                if len(self.main_army_left) > 0:
                    targets = self.main_army_left_info[self.main_army_left[0]].targets.copy()
                else:
                    targets = []
                    print("Warning adding to empty main army left")
                self.main_army_left.append(unit.tag)
                self.main_army_left_info[unit.tag] = ArmyUnitInfo(targets, unit.type_id)
            else:
                if len(self.main_army_right) > 0:
                    targets = self.main_army_right_info[self.main_army_right[0]].targets.copy()
                else:
                    targets = []
                    print("Warning adding to empty main army right")
                self.main_army_right.append(unit.tag)
                self.main_army_right_info[unit.tag] = ArmyUnitInfo(targets, unit.type_id)

    async def on_unit_type_changed(self, unit, previous_type):
        if unit.type_id == OVERSEER:
            self.add_new_overseer(unit.tag)
    
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
        elif building.type_id == UnitTypeId.CREEPTUMOR or building.type_id == UnitTypeId.CREEPTUMORBURROWED or building.type_id == UnitTypeId.CREEPTUMORQUEEN:
            self.current_creep_tumor_tags.append(building.tag)
    
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

        if unit_tag in self.main_army_left:
            self.main_army_left.remove(unit_tag)
            if self.main_army_left_info.pop(unit_tag, None) == None:
                print("Error unit tag not in main army left info")
        if unit_tag in self.main_army_right:
            self.main_army_right.remove(unit_tag)
            if self.main_army_right_info.pop(unit_tag, None) == None:
                print("Error unit tag not in main army right info")
        
        if unit_tag in [self.overseer_defense, self.overseer_left, self.overseer_right]:
            self.remove_overseer(unit_tag)
        
    def convert_location(self, location):
        if self.start_location == Point2((143.5, 32.5)):
            return Point2(location)
        else:
            return Point2((143.5, 32.5)) - Point2(location) + Point2((40.5, 131.5))

    def place_drone(self, drone):
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































