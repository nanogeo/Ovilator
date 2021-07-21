
from dijkstra import Graph
from sc2.position import Point2


"""
class MapNameLocations:
    def convert_location(self, location):
        if self.start_location == Point2((143.5, 32.5)):
            return Point2(location)
        else:
            return Point2((143.5, 32.5)) - Point2(location) + Point2((40.5, 131.5))

    def __init__(self, start_location):
        self.start_location = start_location
        self.army_positions = List all nodes to make map graph
        self.army_position_links = List of lists of all links to make map graph
        self.map_graph = Graph()
            for i in range(0, len(self.army_position_links)):
                for j in range(0, len(self.army_position_links[i])):
                    self.map_graph.add_edge(i, self.army_position_links[i][j], self.army_positions[i].distance_to(self.army_positions[self.army_position_links[i][j]]))

        self.possible_attack_points = List indecies of closest points in army_positions to out bases
        self.enemy_launch_points = List indicies of closest points to enemy bases
        self.army_defense_points_left = List positions for main_army_left to wait for attacks at each spossible_attack_points
        self.army_defense_points_right = See above for main_army_right
        self.army_consolidation_point_left = Point2 main waiting point for main_army_left
        self.army_consolidation_point_right = See above for main_army_right


    """

class LightShadeLocations:

    def convert_location(self, location):
        if self.start_location == Point2((143.5, 32.5)):
            return Point2(location)
        else:
            return Point2((143.5, 32.5)) - Point2(location) + Point2((40.5, 131.5))

    def __init__(self, start_location):
        self.start_location = start_location

        # Map
        self.army_positions = [self.convert_location((132, 78)),
                                self.convert_location((119, 94)),
                                self.convert_location((146, 94)),
                                self.convert_location((132, 141)),
                                self.convert_location((54, 23)),
                                self.convert_location((92, 125)),
                                self.convert_location((72, 97)),
                                self.convert_location((125, 119)),
                                self.convert_location((111, 63)),
                                self.convert_location((97, 48)),
                                self.convert_location((82, 113)),
                                self.convert_location((86, 61)),
                                self.convert_location((34, 39)),
                                self.convert_location((112, 129)),
                                self.convert_location((50, 57)),
                                self.convert_location((106, 81)),
                                self.convert_location((99, 104)),
                                self.convert_location((66, 72)),
                                self.convert_location((150, 127)),
                                self.convert_location((79, 82)),
                                self.convert_location((73, 35)),
                                self.convert_location((134, 106)),
                                self.convert_location((61, 44)),
                                self.convert_location((91, 33))]
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
        self.map_graph = Graph()
        for i in range(0, len(self.army_position_links)):
            for j in range(0, len(self.army_position_links[i])):
                self.map_graph.add_edge(i, self.army_position_links[i][j], self.army_positions[i].distance_to(self.army_positions[self.army_position_links[i][j]]))

        self.new_map_points = [(109, 90),
                                (104, 131),
                                (122, 93),
                                (108, 50),
                                (115, 69),
                                (104, 108),
                                (111, 101),
                                (133, 105),
                                (127, 100),
                                (111, 77),
                                (100, 51),
                                (103, 85),
                                (119, 62),
                                (141, 92),
                                (109, 68),
                                (99, 80),
                                (113, 125),
                                (103, 41),
                                (112, 132),
                                (116, 118),
                                (146, 119),
                                (123, 116),
                                (141, 130),
                                (136, 136),
                                (94, 111),
                                (116, 96),
                                (111, 84),
                                (138, 84),
                                (94, 99),
                                (92, 82),
                                (132, 70),
                                (103, 76),
                                (119, 137),
                                (115, 89),
                                (129, 112),
                                (109, 59),
                                (141, 110),
                                (96, 30),
                                (125, 84),
                                (102, 94),
                                (129, 64),
                                (87, 33),
                                (93, 42),
                                (99, 103),
                                (138, 66),
                                (128, 140),
                                (140, 100),
                                (108, 112),
                                (131, 78), # mid
                                (75, 74),  # mid
                                (80, 33),
                                (62, 71),
                                (76, 114),
                                (69, 95),
                                (80, 56),
                                (73, 63),
                                (51, 59),
                                (57, 64),
                                (73, 87),
                                (84, 113),
                                (81, 79),
                                (65, 102),
                                (43, 72),
                                (75, 96),
                                (85, 84),
                                (71, 39),
                                (81, 123),
                                (72, 32),
                                (68, 46),
                                (38, 45),
                                (61, 48),
                                (43, 34),
                                (48, 28),
                                (90, 53),
                                (68, 68),
                                (73, 80),
                                (46, 80),
                                (90, 65),
                                (92, 82),
                                (52, 94),
                                (81, 88),
                                (65, 27),
                                (69, 75),
                                (55, 52),
                                (75, 105),
                                (43, 54),
                                (88, 134),
                                (59, 80),
                                (82, 70),
                                (55, 100),
                                (97, 131),
                                (91, 122),
                                (85, 61),
                                (46, 98),
                                (56, 24),
                                (44, 64),
                                (76, 52),
                                (53, 86)]
        self.new_map_edges = [[11, 25, 26, 33, 39], # 0
                                [16, 18, 90],
                                [8, 25, 33, 38],
                                [10, 17, 35],
                                [9, 12, 14],
                                [6, 24, 43, 47], # 5
                                [5, 25, 43, 47],
                                [8, 34, 36, 46],
                                [2, 7, 25, 34, 46],
                                [4, 14, 31, 26],
                                [3, 17, 35, 42, 73], # 10
                                [0, 15, 26, 39],
                                [4, 35, 40],
                                [27, 46],
                                [4, 9, 35],
                                [11, 29, 31], # 15
                                [1, 18, 19, 32],
                                [3, 10, 37, 42],
                                [1, 16, 32],
                                [16, 21], # add 47 after rocks
                                [22, 36], # 20
                                [19, 34],
                                [20, 23],
                                [22, 45],
                                [5, 43, 59, 91],
                                [0, 2, 6, 8, 33], # 25
                                [0, 9, 11, 31, 33],
                                [13, 38, 48],
                                [39, 43],
                                [15, 64],
                                [40, 44, 48], # 30
                                [9, 15, 26],
                                [16, 18, 45],
                                [0, 2, 25, 26, 38],
                                [7, 8, 21, 36],
                                [3, 10, 12, 14], # 35
                                [7, 20, 34, 46],
                                [17, 41, 42],
                                [2, 27, 33, 48],
                                [0, 11, 28, 43],
                                [12, 30, 44], # 40
                                [37, 42, 50],
                                [10, 17, 37, 41, 73],
                                [5, 6, 24, 28, 39],
                                [30, 40],
                                [23, 32], # 45
                                [7, 8, 13, 36],
                                [5, 6], # add 19 after rocks
                                [27, 30, 38],
                                [60, 74, 75, 82, 88],
                                [41, 65, 67], # 50
                                [57, 74, 82, 87],
                                [59, 66, 84],
                                [58, 61, 63],
                                [55, 73, 92, 96],
                                [54, 74, 92, 96], # 55
                                [57, 83, 85, 95],
                                [51, 56, 74, 83, 95],
                                [53, 63, 75, 80],
                                [24, 52, 66, 84, 91],
                                [49, 64, 75, 88], # 60
                                [53, 84, 89],
                                [76, 95],
                                [53, 58, 80, 84],
                                [29, 60, 80],
                                [50, 67, 68, 81], # 65
                                [52, 59, 86, 91],
                                [50, 65, 81],
                                [65, 70], # add 96 after rocks
                                [71, 85],
                                [68, 83], # 70
                                [69, 72],
                                [71, 94],
                                [10, 42, 54, 92],
                                [49, 51, 55, 57, 82],
                                [49, 58, 60, 80, 82], # 75
                                [62, 87, 97],
                                [88, 92],
                                [],
                                [89, 93, 97],
                                [58, 63, 64, 75], # 80
                                [65, 67, 94],
                                [49, 51, 74, 75, 87],
                                [56, 57, 70, 85],
                                [52, 59, 61, 63],
                                [56, 69, 83, 95], # 85
                                [66, 90, 91],
                                [51, 76, 82, 97],
                                [49, 60, 77, 92],
                                [61, 79, 93],
                                [1, 86, 91], # 90
                                [24, 59, 66, 86, 90],
                                [54, 55, 73, 77, 88],
                                [79, 89],
                                [72, 81],
                                [56, 57, 62, 85], # 95
                                [54, 55], # add 68 after rocks
                                [76, 79, 87]]
        

        # Bases


        # Army
        self.possible_attack_points = [23, 9, 8, 0, 2]
        self.enemy_launch_points = [5, 6, 10, 14, 17]
        self.army_defense_points_left = [self.convert_location((51, 21)),
                                        self.convert_location((97, 22)),
                                        self.convert_location((106, 39)),
                                        self.convert_location((140, 61)),
                                        self.convert_location((137, 78))]
        self.army_defense_points_right = [self.convert_location((114, 54)),
                                        self.convert_location((124, 62)),
                                        self.convert_location((125, 98)),
                                        self.convert_location((134, 106)),
                                        self.convert_location((146, 133))]
        self.army_consolidation_point_left = self.convert_location((100, 42))
        self.army_consolidation_point_right = self.convert_location((130, 78))
        self.rally_points = [self.convert_location((114, 131)),
                            self.convert_location((84, 117)),
                            self.convert_location((40, 70)),
                            self.convert_location((68, 68)),
                            self.convert_location((101, 106)),
                            self.convert_location((60, 46)),
                            self.convert_location((93, 123)),
                            self.convert_location((80, 81))]
        


        """ 
        self.muta_attack_positions = [self.convert_location((57, 41)),
                                    self.convert_location((35, 102)),
                                    self.convert_location((61, 113)),
                                    self.convert_location((32, 69)),
                                    self.convert_location((32, 38)),
                                    self.convert_location((76, 139)),
                                    self.convert_location((37, 134))]
        self.muta_rally_points = [self.convert_location((24, 16)),
                                self.convert_location((106, 148)),
                                self.convert_location((24, 86)),
                                self.convert_location((63, 129)),
                                self.convert_location((64, 148)),
                                self.convert_location((24, 54)),
                                self.convert_location((76, 16)),
                                self.convert_location((24, 148)),
                                self.convert_location((24, 116))]

        self.nydus_positions = [self.convert_location((30.5, 77.5)),
                                self.convert_location((75.5, 130.5)),
                                self.convert_location((103.5, 111.5)),
                                self.convert_location((33.5, 48.5)),
                                self.convert_location((109.5, 135.5)),
                                self.convert_location((57.5, 44.5)),
                                self.convert_location((83.5, 85.5)),
                                self.convert_location((60.5, 132.5)),
                                self.convert_location((42.5, 141.5)),
                                self.convert_location((46.5, 23.5)),
                                self.convert_location((88.5, 98.5)),
                                self.convert_location((74.5, 55.5))]
        """

        
        # scouting

        self.scouting_path = [[self.convert_location((105, 28)), self.convert_location((75, 32)), self.convert_location((55, 23)), self.convert_location((35, 38)), self.convert_location((36, 69))],
                               [self.convert_location((108, 81)), self.convert_location((75, 32)), self.convert_location((51, 57)), self.convert_location((66, 69))],
                               [self.convert_location((77, 54)), self.convert_location((92, 67)), self.convert_location((78, 83))],
                               [self.convert_location((91, 97)), self.convert_location((105, 109)), self.convert_location((72, 96))],
                               [self.convert_location((118, 92)), self.convert_location((128, 122)), self.convert_location((113, 118)), self.convert_location((64, 107))],
                               [self.convert_location((149, 95)), self.convert_location((150, 126)), self.convert_location((129, 141)), self.convert_location((81, 136))]]

        self.main_scout_path = [self.convert_location((53, 133)), self.convert_location((50, 125)), self.convert_location((36, 125)), self.convert_location((37, 137))]


        # buildings

        
        self.spore_positions = [self.convert_location((123, 54)),
                                self.convert_location((155, 120)),
                                self.convert_location((155, 132)),
                                self.convert_location((119, 46)),
                                self.convert_location((104, 20)),
                                self.convert_location((152, 68)),
                                self.convert_location((152, 33)),
                                self.convert_location((142, 25)),
                                self.convert_location((152, 88)),
                                self.convert_location((152, 101)),
                                self.convert_location((113, 28)),
                                self.convert_location((151, 56))]
        
        self.creep_locations = [self.convert_location((140, 92)),
                                self.convert_location((127, 82)),
                                self.convert_location((130, 65)),
                                self.convert_location((141, 42)),
                                self.convert_location((115, 65)),
                                self.convert_location((139, 65))]
        """
        self.expos = [self.convert_location((143.5, 32.5)),    # BR main
                    self.convert_location((148.5, 125.5)),     # BR inline 5th
                    self.convert_location((79.5, 136.5)),      # TL triangle 5th
                    self.convert_location((36.5, 69.5)),       # TL inline 3rd
                    self.convert_location((59.5, 43.5)),       # TL middle
                    self.convert_location((119.5, 53.5)),      # BR triangle 3rd
                    self.convert_location((35.5, 38.5)),       # TL inline 5th
                    self.convert_location((38.5, 102.5)),      # TL natural
                    self.convert_location((124.5, 120.5)),     # BR middle
                    self.convert_location((64.5, 110.5)),      # TL triangle 3rd
                    self.convert_location((145.5, 61.5)),      # BR natural
                    self.convert_location((147.5, 94.5)),      # BR inline 3rd
                    self.convert_location((104.5, 27.5)),      # BR triangle 5th
                    self.convert_location((40.5, 131.5))]       # TL main

        # overlords

        self.overlord_positions = [ self.convert_location((42, 92)),	#	enemy natural pillar
                                    self.convert_location((122, 78)),	#	natural enterance pillar
                                    self.convert_location((64, 147)),	#	near enemy main
                                    self.convert_location((62, 86)),	#	enemy natural exit pillar
                                    self.convert_location((46, 71)),	#	enemy inline 3rd
                                    self.convert_location((70, 103)),	#	enemy triangle 3rd enemy natural exit 2
                                    self.convert_location((24, 85)),	#	enemy natural deadspace
                                    self.convert_location((69, 73)),	#	enemy natural exit
                                    self.convert_location((84, 50)),	#	close left route pillar
                                    self.convert_location((105, 95)),	#	close right route 2
                                    self.convert_location((24, 147)),	#	behind enemy main
                                    self.convert_location((86, 126)),	#	enemy 5th base
                                    self.convert_location((159, 81)),	#	close deadspace
                                    self.convert_location((119, 19)),	#	close opposite deadspace
                                    self.convert_location((100, 114)),	#	close right route pillar
                                    self.convert_location((90, 90)),	#	right middle route pillar - replace
                                    self.convert_location((94, 74)),	#	left middle route pillar - replace
                                    self.convert_location((64, 34)),	#	farthest left route pillar
                                    self.convert_location((40, 60)),	#	enemy inline 3rd pillar - move to
                                    self.convert_location((42, 35)),	#	enemy inline 4th
                                    self.convert_location((60, 56)),	#	enemy inline 3rd exit pillar
                                    self.convert_location((77, 19)),	#	far opposite deadspace
                                    self.convert_location((106, 146)),	#	far right deadspace
                                    self.convert_location((120, 130)),	#	far right route pillar - add
                                    self.convert_location((159, 112)),	#	far deadspace
                                    self.convert_location((25, 54)),	#	enemy inline 3rd space
                                    self.convert_location((153, 143)),	#	right corner
                                    self.convert_location((31, 22)), 	#	left corner
                                    self.convert_location((60, 56)),	#	enemy inline 3rd exit pillar
                                    self.convert_location((58, 119))]	#	elevator
        
        """