# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 23:53:47 2020

@author: hocke
"""

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.position import Point2, Point3
from sc2.constants import EGG, DRONE, QUEEN, ZERGLING, BANELING, ROACH, RAVAGER, HYDRALISK, LURKER, MUTALISK, CORRUPTOR, BROODLORD, OVERLORD, OVERSEER, INFESTOR, SWARMHOSTMP, LARVA, VIPER, ULTRALISK
from sc2.constants import ROACHBURROWED
from sc2.constants import HATCHERY, LAIR, HIVE, EXTRACTOR, SPAWNINGPOOL, ROACHWARREN, HYDRALISKDEN, LURKERDEN, SPIRE, GREATERSPIRE, EVOLUTIONCHAMBER, SPORECRAWLER, SPINECRAWLER, INFESTATIONPIT, BANELINGNEST, CREEPTUMOR, NYDUSNETWORK, ULTRALISKCAVERN, CREEPTUMORBURROWED, CREEPTUMORQUEEN
from sc2.constants import PROBE, SCV
from sc2.constants import NEXUS
from sc2.constants import COMMANDCENTER, ORBITALCOMMAND, PLANETARYFORTRESS
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.buff_id import BuffId
from s2clientprotocol import raw_pb2 as raw_pb
from s2clientprotocol import sc2api_pb2 as sc_pb

class ArmyComp:
    LING_BANE_HYDRA = 1
    ROACH_HYDRA = 2
    LING_BANE_MUTA = 3

class ArmyState:
    CONSOLIDATING = 1
    RALLYING = 2
    ATTACKING = 3
    PROTECTING = 4

class MutaGroupState:
    CONSOLIDATING = 1
    MOVING_TO_RALLY = 2
    MOVING_TO_ATTACK = 3
    ATTACKING = 4
    RETREATING = 5
    
    

class ZergBot(sc2.BotAI):
    def __init__(self):
        self.has_debug = False
        self.debug_interval = 10
        self.unit_command_uses_self_do = True
        self.injecting_queens = []
        self.creep_queens = []
        self.inactive_creep_tumors = []
        self.build_order = [(0, self.build_drone),
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
                            (109, self.build_drone),
                            (110, self.send_ling_scouts),
                            (120, self.build_drone)]
        """
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
        self.creep_locations = [(139.618896484375, 92.466552734375),
                                (127.156982421875, 81.634765625),
                                (129.79638671875, 64.93896484375),
                                (141.262451171875, 42.2890625),
                                (114.623291015625, 65.232421875),
                                (139.1455078125, 65.218017578125)]
        self.creep_spread_to = []
        self.updated_creep = False
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
        self.rally_points = [(114, 131),
                            (84, 117),
                            (40, 70),
                            (68, 68),
                            (101, 106),
                            (60, 46),
                            (93, 123),
                            (80, 81)]
        self.army_spot = (127, 81)
        self.attack_position = None
        self.rally_point = None
        self.army_unit_tags = []
        self.zergling_scout_tags = [None]*6
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
        self.burrow_researched = False
        self.burrow_movement_researched = False
        self.army_state = ArmyState.CONSOLIDATING
        
        self.army_composition = ArmyComp.LING_BANE_MUTA
        
        self.enemy_army_position = None
        
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
        
    
    async def on_step(self, iteration):
        await self.display_debug_info()
        await self.distribute_workers()
        await self.execute_build()
        await self.get_upgrades()
        await self.inject_larva()
        await self.update_creep()
        await self.spread_creep()
        await self.place_creep_tumors()
        await self.position_overlords()
        await self.scouting()
        await self.update_enemy_units()
        await self.track_enemy_army_position()
        if self.build_step >= len(self.build_order):
            await self.update_building_need()
            await self.use_larva()
            await self.make_expansions()
            await self.expand_tech()
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
        if self.minerals >= 300:
            self.last_expansion_time = self.time
            await self.expand_now()
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
            ovi_tag = self.position_to_ovi_dict[self.convert_location(Point2(self.overlord_positions[6]))]
            if self.units.tags_in([ovi_tag]):
                self.position_new_overlord(self.units.tags_in([ovi_tag])[0])
        if new_expos[2]:
            ovi_tag = self.position_to_ovi_dict[self.convert_location(Point2(self.overlord_positions[7]))]
            if self.units.tags_in([ovi_tag]):
                self.position_new_overlord(self.units.tags_in([ovi_tag])[0])
        if new_expos[3]:
            ovi_tag1 = self.position_to_ovi_dict[self.convert_location(Point2(self.overlord_positions[8]))]
            if self.units.tags_in([ovi_tag1]):
                self.position_new_overlord(self.units.tags_in([ovi_tag1])[0])
            ovi_tag2 = self.position_to_ovi_dict[self.convert_location(Point2(self.overlord_positions[12]))]
            if self.units.tags_in([ovi_tag2]):
                self.position_new_overlord(self.units.tags_in([ovi_tag2])[0])
        if new_expos[4]:
            ovi_tag = self.position_to_ovi_dict[self.convert_location(Point2(self.overlord_positions[9]))]
            if self.units.tags_in([ovi_tag]):
                self.position_new_overlord(self.units.tags_in([ovi_tag])[0])
        if new_expos[5]:
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
        gates = 0
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
                 robo_bays += 1
        #respond to scouts
        if dark_shrines >= 1:
            self.lair_need = 100
        if stargates == 1:
            # need more queens
            self.hydra_den_need = 100
        elif stargates > 1:
            self.hydra_den_need = 100
        if fleet_beacons:
            self.spire_need == 100
   
    async def update_units_needs(self):
        #drones
        if len(self.townhalls) < 3 and self.time < 240:
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
                self.zergling_need = 60
            #banes
            self.baneling_need = len(self.units(ZERGLING)) / 2
            #hydras
            if len(self.structures(HYDRALISKDEN)) > 0:
                if self.supply_workers + self.already_pending(DRONE) < 80:
                    self.hydralisk_need = supply * 0.25
                else:
                    self.hydralisk_need = 30
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
        # the enemy has the same number of bases as us
        if sum(self.enemy_expos) + 1 >= len(self.townhalls) + self.already_pending(HATCHERY) or self.time >= self.last_expansion_time + 180:
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
            ling = self.units.tags_in([self.zergling_scout_tags[i]])[0]
            for j in range(0, len(self.scouting_path[i])):
                self.do(ling.move(self.convert_location(Point2(self.scouting_path[i][j])), True))
        return True
    
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
    
    async def place_creep_tumors(self):
        for queen in self.creep_queens:
            if self.units.tags_in([queen])[0].energy >= 25 and self.units.tags_in([queen])[0].is_idle and len(self.creep_spread_to) > 0 :
                self.do(self.units.tags_in([queen])[0](AbilityId.BUILD_CREEPTUMOR_QUEEN, Point2(self.creep_spread_to.pop(0))))
                
                
    def find_creep_spots(self):
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
        if self.time > 600:
            return
        if not self.updated_creep and int(self.time) % 2 == 0:
            self.updated_creep = True
            self.creep_spread_to = self.find_creep_spots()
        elif self.updated_creep and int(self.time) % 2 == 1:
            self.updated_creep = False
   
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
################# MICRO ################
########################################

    async def micro(self):
        need_to_protect = None
        # are we being attacked right now?
        for enemy in self.enemy_units.exclude_type([DRONE, PROBE, SCV]):
            for hatch in self.townhalls:
                if enemy.distance_to(hatch) < 20:
                    need_to_protect = enemy.position
        if self.army_composition == ArmyComp.LING_BANE_MUTA:
            await self.micro_mutas()
        
        if self.army_state == ArmyState.CONSOLIDATING:
            if need_to_protect:
                self.army_state = ArmyState.PROTECTING
                for unit in self.units.exclude_type([LARVA, DRONE, QUEEN, OVERLORD, MUTALISK]):
                    self.do(unit.attack(need_to_protect))
            # move all units to the consolidation point
            for unit in self.units.exclude_type([LARVA, DRONE, QUEEN, OVERLORD]).tags_not_in(self.zergling_scout_tags + self.muta_group_tags):
                if unit.distance_to(Point2(self.convert_location(self.army_spot))) > 10 and unit.is_idle:
                    self.do(unit.move(Point2(self.convert_location(self.army_spot))))
            # if we have more than 90 army supply ready then go to the rally point
            if sum(self.calculate_supply_cost(unit.type_id) for unit in self.units.exclude_type([LARVA, DRONE, QUEEN, OVERLORD, MUTALISK]).tags_not_in(self.zergling_scout_tags)) >= 90:
                self.army_state = ArmyState.RALLYING
                await self.find_attack_and_rally_points()
                print("rally to " + str(self.rally_point))
                self.army_unit_tags = []
                for unit in self.units.exclude_type([LARVA, DRONE, QUEEN, OVERLORD, MUTALISK]).tags_not_in(self.zergling_scout_tags):
                    self.army_unit_tags.append(unit.tag)
                    self.do(unit.attack(Point2(self.rally_point)))
        elif self.army_state == ArmyState.RALLYING:
            # if we're attacked while we're launching an attack then go back to defend
            # TODO determine if we need to defend and how much with
            if need_to_protect:
                self.army_state = ArmyState.PROTECTING
                for unit in self.units.exclude_type([LARVA, DRONE, QUEEN, OVERLORD, MUTALISK]).tags_not_in(self.zergling_scout_tags):
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
                for unit in self.units.exclude_type([LARVA, DRONE, QUEEN, OVERLORD, MUTALISK]).tags_not_in(self.army_unit_tags + self.zergling_scout_tags):
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
        """
        if sum(self.calculate_supply_cost(unit.type_id) for unit in self.units.exclude_type([DRONE, QUEEN, OVERLORD])) >= 90:
            if self.enemy_expos[5] == 1:
                print("attack middle base")
                for unit in self.units.not_structure.exclude_type([DRONE, QUEEN, OVERLORD]):
                    self.do(unit.attack(Point2(self.convert_location(self.expos[4]))))
            elif self.enemy_expos[4] == 1:
                print("attack triangle 5th")
                for unit in self.units.not_structure.exclude_type([DRONE, QUEEN, OVERLORD]):
                    self.do(unit.attack(Point2(self.convert_location(self.expos[2]))))
            elif self.enemy_expos[3] == 1:
                print("attack inline 5th")
                for unit in self.units.not_structure.exclude_type([DRONE, QUEEN, OVERLORD]):
                    self.do(unit.attack(Point2(self.convert_location(self.expos[6]))))
            elif self.enemy_expos[2] == 1:
                print("attack triangle 3rd")
                for unit in self.units.not_structure.exclude_type([DRONE, QUEEN, OVERLORD]):
                    self.do(unit.attack(Point2(self.convert_location(self.expos[9]))))
            elif self.enemy_expos[1] == 1:
                print("attack inline 3rd")
                for unit in self.units.not_structure.exclude_type([DRONE, QUEEN, OVERLORD]):
                    self.do(unit.attack(Point2(self.convert_location(self.expos[3]))))
            elif self.enemy_expos[0] == 1:
                print("attack natural")
                for unit in self.units.not_structure.exclude_type([DRONE, QUEEN, OVERLORD]):
                    self.do(unit.attack(Point2(self.convert_location(self.expos[7]))))
            else:
                print("attack anything")
                for unit in self.units.not_structure.exclude_type([DRONE, QUEEN, OVERLORD]):
                    self.do(unit.attack(self.enemy_structures().random.position))
                
        elif len(self.enemy_units) > 0 and len(self.units.exclude_type([DRONE, QUEEN, OVERLORD])) > 1:
            for enemy in self.enemy_units:
                for hatch in self.townhalls:
                    if enemy.distance_to(hatch) < 20:
                        for unit in self.units.exclude_type([DRONE, QUEEN, OVERLORD]):
                            self.do(unit.attack(enemy.position))
                        return
        """
    
                    
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
                
    
########################################
################# MACRO ################
########################################

    async def build_roach_warren(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.build_location = None
            self.builder_drone = self.select_build_worker(self.start_location).tag
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
        elif self.build_location == None:
            print("no place")
            builder = self.units.tags_in([self.builder_drone])[0]
            pool_location = self.structures(SPAWNINGPOOL)[0].position
            self.build_location = await self.find_placement(UnitTypeId.ROACHWARREN, near = pool_location, max_distance = 10)
            if not await self.can_place(ROACHWARREN, self.build_location):
                self.build_location = None
        #elif not await self.can_place(ROACHWARREN, self.build_location):
            #print("invalid place")
            #self.build_location = None
        elif await self.can_place(ROACHWARREN, self.build_location):
            builder = self.units.tags_in([self.builder_drone])[0]
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.build(ROACHWARREN, self.build_location))
        
    
    async def build_baneling_nest(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.build_location = None
            self.builder_drone = self.select_build_worker(self.start_location).tag
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
        elif self.build_location == None:
            print("no place")
            builder = self.units.tags_in([self.builder_drone])[0]
            pool_location = self.structures(SPAWNINGPOOL)[0].position
            self.build_location = await self.find_placement(UnitTypeId.BANELINGNEST, near = pool_location, max_distance = 10)
            if not await self.can_place(ROACHWARREN, self.build_location):
                self.build_location = None
        #elif not await self.can_place(BANELINGNEST, self.build_location):
            #print("invalid place")
            #self.build_location = None
        elif await self.can_place(BANELINGNEST, self.build_location):
            builder = self.units.tags_in([self.builder_drone])[0]
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.build(BANELINGNEST, self.build_location))
    
    async def build_evolution_chamber(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.build_location = None
            self.builder_drone = self.select_build_worker(self.start_location).tag
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
        elif self.build_location == None:
            print("no place")
            builder = self.units.tags_in([self.builder_drone])[0]
            pool_location = self.structures(SPAWNINGPOOL)[0].position
            self.build_location = await self.find_placement(UnitTypeId.EVOLUTIONCHAMBER, near = pool_location, max_distance = 10)
            if not await self.can_place(ROACHWARREN, self.build_location):
                self.build_location = None
        #elif not await self.can_place(EVOLUTIONCHAMBER, self.build_location):
            #print("invalid place")
            #self.build_location = None
        elif await self.can_place(EVOLUTIONCHAMBER, self.build_location):
            builder = self.units.tags_in([self.builder_drone])[0]
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.build(EVOLUTIONCHAMBER, self.build_location))
            
    async def build_hydralisk_den(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.build_location = None
            self.builder_drone = self.select_build_worker(self.start_location).tag
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
        elif self.build_location == None:
            print("no place")
            builder = self.units.tags_in([self.builder_drone])[0]
            pool_location = self.structures(SPAWNINGPOOL)[0].position
            self.build_location = await self.find_placement(UnitTypeId.HYDRALISKDEN, near = pool_location, max_distance = 10)
            if not await self.can_place(HYDRALISKDEN, self.build_location):
                self.build_location = None
        #elif not await self.can_place(HYDRALISKDEN, self.build_location):
            #print("invalid place")
            #self.build_location = None
        elif await self.can_place(HYDRALISKDEN, self.build_location):
            builder = self.units.tags_in([self.builder_drone])[0]
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.build(HYDRALISKDEN, self.build_location))
            
    async def build_infestation_pit(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.build_location = None
            self.builder_drone = self.select_build_worker(self.start_location).tag
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
        elif self.build_location == None:
            print("no place")
            builder = self.units.tags_in([self.builder_drone])[0]
            pool_location = self.structures(SPAWNINGPOOL)[0].position
            self.build_location = await self.find_placement(UnitTypeId.INFESTATIONPIT, near = pool_location, max_distance = 10)
            if not await self.can_place(INFESTATIONPIT, self.build_location):
                self.build_location = None
        #elif not await self.can_place(INFESTATIONPIT, self.build_location):
            #print("invalid place")
            #self.build_location = None
        elif await self.can_place(INFESTATIONPIT, self.build_location):
            builder = self.units.tags_in([self.builder_drone])[0]
            height = self.get_terrain_z_height(self.build_location)
            self._client.debug_sphere_out(Point3((self.build_location[0], self.build_location[1], height)), 1, color = Point3((255, 255, 0)))
            self.do(builder.build(INFESTATIONPIT, self.build_location))
             
    async def build_spire(self):
        if self.builder_drone == None or len(self.units.tags_in([self.builder_drone])) == 0:
            self.build_location = None
            self.builder_drone = self.select_build_worker(self.start_location).tag
            if len(self.units.tags_in([self.builder_drone])) == 0:
                self.builder_drone = None
                return False
        elif self.build_location == None:
            print("no place")
            builder = self.units.tags_in([self.builder_drone])[0]
            pool_location = self.structures(SPAWNINGPOOL)[0].position
            self.build_location = await self.find_placement(UnitTypeId.SPIRE, near = pool_location, max_distance = 10)
            if not await self.can_place(SPIRE, self.build_location):
                self.build_location = None
        #elif not await self.can_place(SPIRE, self.build_location):
            #print("invalid place")
            #self.build_location = None
        elif await self.can_place(SPIRE, self.build_location):
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
                    if worker is None:
                        break
                    self._client.debug_sphere_out(Point3((vespene.position[0], vespene.position[1], self.get_terrain_z_height(vespene.position))), 1, color = Point3((255, 255, 0)))
                    self.do(worker.build(EXTRACTOR, vespene))
                    return True
        return False
    
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
            elif self.supply_workers + self.already_pending(DRONE) < self.drone_need:
                if self.minerals >= 50:
                    if len(self.units(ZERGLING)) + self.already_pending(ZERGLING) < self.zergling_need:
                        print("bad")
                    self.do(larva.train(DRONE))
        if self.pending_upgrade != 2:
            for zergling in self.units(ZERGLING).idle:
                if len(self.units(BANELING)) + self.already_pending(BANELING) < self.baneling_need:
                    if self.minerals >= 25 and self.vespene >= 25:
                        self.do(zergling(AbilityId.MORPHZERGLINGTOBANELING_BANELING))

    async def make_expansions(self):
        if self.expansion_need == 100:
            if self.minerals >= 300:
                self.last_expansion_time = self.time
                await self.expand_now()
        """
        if self.time > 180 and len(self.structures(HATCHERY)) < 3:
            await self.expand_now()
        
        if not self.already_pending(HATCHERY):
            await self.expand_now()
        """
            
    async def expand_tech(self):
        if self.time >= 240:
            await self.build_extractor()
            if self.army_composition == ArmyComp.LING_BANE_HYDRA or self.army_composition == ArmyComp.LING_BANE_MUTA:
                if self.can_afford(BANELINGNEST) and len(self.structures(BANELINGNEST)) == 0:
                    await self.build_baneling_nest()
            elif self.army_composition == ArmyComp.ROACH_HYDRA:
                if self.can_afford(ROACHWARREN) and len(self.structures(ROACHWARREN)) == 0:
                    await self.build_roach_warren()
        if self.supply_workers > 40 or self.time > 240:
            if len(self.structures(LAIR)) + len(self.structures(HIVE)) == 0 and not self.already_pending(LAIR):
                hatch = self.structures(HATCHERY)[0]
                for ability in await self.get_available_abilities(hatch):
                    if ability == AbilityId.UPGRADETOLAIR_LAIR:
                        self.do(hatch(AbilityId.UPGRADETOLAIR_LAIR))
        if self.supply_workers > 80 or self.time > 480:
            if len(self.structures(HIVE)) == 0 and not self.already_pending(HIVE):
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
                if self.can_afford(INFESTATIONPIT) and len(self.structures(INFESTATIONPIT)) == 0 and self.time > 300 and len(self.structures({SPIRE, GREATERSPIRE})) > 0:
                    await self.build_infestation_pit()
    
    async def build_extractor(self):
        if self.vespene > 500 or (self.time < 360 and len(self.structures(EXTRACTOR)) >= 2):
            return
        for hatch in self.structures({HATCHERY, LAIR, HIVE}).ready:
            if hatch.assigned_harvesters > hatch.ideal_harvesters - 2 or (self.vespene < 100 and self.already_pending(EXTRACTOR) < 2):
                vespenes = self.vespene_geyser.closer_than(10.0, hatch)
                for vespene in vespenes:
                    if self.can_afford(EXTRACTOR) and not self.structures(EXTRACTOR).closer_than(1.0, vespene).exists:
                        worker = self.select_build_worker(vespene.position)
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
        if self.army_composition == ArmyComp.LING_BANE_HYDRA or self.army_composition == ArmyComp.ROACH_HYDRA:
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
        if self.army_composition == ArmyComp.ROACH_HYDRA:
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
    
    

########################################
################ UTILITY ###############
########################################
    
    async def display_debug_info(self):
        if not self.has_debug and round(self.time) % self.debug_interval == 0:
            self.has_debug = True
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
            if self.expansion_need == 100:
                print("need to expand")
            else:
                 print("enemy bases "  + str(sum(self.enemy_expos) + 1) + " my bases " + str(len(self.townhalls)))
                 print("next expo: " + str(self.last_expansion_time + 180) + " time " + str(self.time))
            print("END DEBUG")
        elif self.has_debug and round(self.time) % self.debug_interval == 1:
            self.has_debug = False
    
    

    async def on_unit_created(self, unit):
        if unit.type_id == UnitTypeId.QUEEN:
            if len(self.injecting_queens) > len(self.creep_queens):
                self.creep_queens.append(unit.tag)
            else:
                self.injecting_queens.append(unit.tag)
            self.spread_inject_queens()
        if unit.type_id == UnitTypeId.OVERLORD:
            self.position_new_overlord(unit)
        if unit.type_id == UnitTypeId.ZERGLING:
            for i in range(0, len(self.zergling_scout_tags)):
                if self.zergling_scout_tags[i] == None:
                    self.zergling_scout_tags[i] = unit.tag
                    break
    
    async def on_building_construction_complete(self, building):
        if building.type_id == UnitTypeId.HATCHERY:
            self.spread_inject_queens()
    
    async def on_building_construction_started(self, unit):
        if unit.type_id == UnitTypeId.HATCHERY:
            self.last_expansion_time = self.time
            
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
        for queen in self.injecting_queens:
            if unit_tag == queen:
                self.injecting_queens.remove(queen)
        for queen in self.creep_queens:
            if unit_tag == queen:
                self.creep_queens.remove(queen)
        for i in range(0, 6):
            if self.zergling_scout_tags[i] == unit_tag:
                self.zergling_scout_tags[i] = None
                break
        for muta in self.muta_group_tags:
            if unit_tag == muta:
                self.muta_group_tags.remove(muta)


    def convert_location(self, location):
        if self.start_location == Point2((143.5, 32.5)):
            return Point2(location)
        else:
            return Point2((143.5, 32.5)) - Point2(location) + Point2((40.5, 131.5))



    async def distribute_workers(self, resource_ratio: float = 2):
        if not self.mineral_field or not self.workers or not self.townhalls.ready:
            return
        worker_pool = [worker for worker in self.workers.idle]
        bases = self.townhalls.ready
        gas_buildings = self.gas_buildings.ready

        # list of places that need more workers
        deficit_mining_places = []

        for mining_place in bases | gas_buildings:
            difference = mining_place.surplus_harvesters
            # perfect amount of workers, skip mining place
            if not difference:
                continue
            if mining_place.has_vespene:
                # get all workers that target the gas extraction site
                # or are on their way back from it
                local_workers = self.workers.filter(
                    lambda unit: unit.order_target == mining_place.tag
                    or (unit.is_carrying_vespene and unit.order_target == bases.closest_to(mining_place).tag)
                )
            else:
                # get tags of minerals around expansion
                local_minerals_tags = {
                    mineral.tag for mineral in self.mineral_field if mineral.distance_to(mining_place) <= 8
                }
                # get all target tags a worker can have
                # tags of the minerals he could mine at that base
                # get workers that work at that gather site
                local_workers = self.workers.filter(
                    lambda unit: unit.order_target in local_minerals_tags
                    or (unit.is_carrying_minerals and unit.order_target == mining_place.tag)
                )
            # too many workers
            if difference > 0:
                for worker in local_workers[:difference]:
                    worker_pool.append(worker)
            # too few workers
            # add mining place to deficit bases for every missing worker
            else:
                deficit_mining_places += [mining_place for _ in range(-difference)]

        # prepare all minerals near a base if we have too many workers
        # and need to send them to the closest patch
        if len(worker_pool) > len(deficit_mining_places):
            all_minerals_near_base = [
                mineral
                for mineral in self.mineral_field
                if any(mineral.distance_to(base) <= 8 for base in self.townhalls.ready)
            ]
        # distribute every worker in the pool
        for worker in worker_pool:
            # as long as have workers and mining places
            if deficit_mining_places:
                # choose only mineral fields first if current mineral to gas ratio is less than target ratio
                if self.vespene and self.minerals / self.vespene < resource_ratio:
                    possible_mining_places = [place for place in deficit_mining_places if not place.vespene_contents]
                # else prefer gas
                else:
                    possible_mining_places = [place for place in deficit_mining_places if place.vespene_contents]
                # if preferred type is not available any more, get all other places
                if not possible_mining_places:
                    possible_mining_places = deficit_mining_places
                # find closest mining place
                current_place = min(deficit_mining_places, key=lambda place: place.distance_to(worker))
                # remove it from the list
                deficit_mining_places.remove(current_place)
                # if current place is a gas extraction site, go there
                if current_place.vespene_contents:
                    self.do(worker.gather(current_place))
                # if current place is a gas extraction site,
                # go to the mineral field that is near and has the most minerals left
                else:
                    local_minerals = (
                        mineral for mineral in self.mineral_field if mineral.distance_to(current_place) <= 8
                    )
                    # local_minerals can be empty if townhall is misplaced
                    target_mineral = max(local_minerals, key=lambda mineral: mineral.mineral_contents, default=None)
                    if target_mineral:
                        self.do(worker.gather(target_mineral))
            # more workers to distribute than free mining spots
            # send to closest if worker is doing nothing
            elif worker.is_idle and all_minerals_near_base:
                target_mineral = min(all_minerals_near_base, key=lambda mineral: mineral.distance_to(worker))
                self.do(worker.gather(target_mineral))
            else:
                # there are no deficit mining places and worker is not idle
                # so dont move him
                pass
    
        
run_game(maps.get("LightshadeLE"), [
        Bot(Race.Zerg, ZergBot()),
        Computer(Race.Terran, Difficulty.VeryHard)
        ], realtime = False)

# Difficulty Easy, Medium, Hard, VeryHard, CheatVision, CheatMoney, CheatInsane

