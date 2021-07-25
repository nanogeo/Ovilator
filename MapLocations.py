
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
		self.new_map_points = [self.convert_location((109, 90)),
								self.convert_location((104, 131)),
								self.convert_location((122, 93)),
								self.convert_location((108, 50)),
								self.convert_location((115, 69)),
								self.convert_location((104, 108)),
								self.convert_location((111, 101)),
								self.convert_location((133, 105)),
								self.convert_location((127, 100)),
								self.convert_location((111, 77)),
								self.convert_location((100, 51)),
								self.convert_location((103, 85)),
								self.convert_location((119, 62)),
								self.convert_location((141, 92)),
								self.convert_location((109, 68)),
								self.convert_location((99, 80)),
								self.convert_location((113, 125)),
								self.convert_location((103, 41)),
								self.convert_location((112, 132)),
								self.convert_location((116, 118)),
								self.convert_location((146, 119)),
								self.convert_location((123, 116)),
								self.convert_location((141, 130)),
								self.convert_location((136, 136)),
								self.convert_location((94, 111)),
								self.convert_location((116, 96)),
								self.convert_location((111, 84)),
								self.convert_location((138, 84)),
								self.convert_location((94, 99)),
								self.convert_location((92, 82)),
								self.convert_location((132, 70)),
								self.convert_location((103, 76)),
								self.convert_location((119, 137)),
								self.convert_location((115, 89)),
								self.convert_location((129, 112)),
								self.convert_location((109, 59)),
								self.convert_location((141, 110)),
								self.convert_location((96, 30)),
								self.convert_location((125, 84)),
								self.convert_location((102, 94)),
								self.convert_location((129, 64)),
								self.convert_location((87, 33)),
								self.convert_location((93, 42)),
								self.convert_location((99, 103)),
								self.convert_location((138, 66)),
								self.convert_location((128, 140)),
								self.convert_location((140, 100)),
								self.convert_location((108, 112)),
								self.convert_location((131, 78)), # mid
								self.convert_location((75, 74)),  # mid
								self.convert_location((80, 33)),
								self.convert_location((62, 71)),
								self.convert_location((76, 114)),
								self.convert_location((69, 95)),
								self.convert_location((80, 56)),
								self.convert_location((73, 63)),
								self.convert_location((51, 59)),
								self.convert_location((57, 64)),
								self.convert_location((73, 87)),
								self.convert_location((84, 113)),
								self.convert_location((81, 79)),
								self.convert_location((65, 102)),
								self.convert_location((43, 72)),
								self.convert_location((75, 96)),
								self.convert_location((85, 84)),
								self.convert_location((71, 39)),
								self.convert_location((81, 123)),
								self.convert_location((72, 32)),
								self.convert_location((68, 46)),
								self.convert_location((38, 45)),
								self.convert_location((61, 48)),
								self.convert_location((43, 34)),
								self.convert_location((48, 28)),
								self.convert_location((90, 53)),
								self.convert_location((68, 68)),
								self.convert_location((73, 80)),
								self.convert_location((46, 80)),
								self.convert_location((90, 65)),
								self.convert_location((92, 82)),
								self.convert_location((52, 94)),
								self.convert_location((81, 88)),
								self.convert_location((65, 27)),
								self.convert_location((69, 75)),
								self.convert_location((55, 52)),
								self.convert_location((75, 105)),
								self.convert_location((43, 54)),
								self.convert_location((88, 134)),
								self.convert_location((59, 80)),
								self.convert_location((82, 70)),
								self.convert_location((55, 100)),
								self.convert_location((97, 131)),
								self.convert_location((91, 122)),
								self.convert_location((85, 61)),
								self.convert_location((46, 98)),
								self.convert_location((56, 24)),
								self.convert_location((44, 64)),
								self.convert_location((76, 52)),
								self.convert_location((53, 86))]
		# TODO remove self if this is unused
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
								[4, 9, 31, 35],
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
								[9, 14, 15, 26],
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

		self.map_graph = Graph()
		for i in range(0, len(self.new_map_edges)):
			point1 = self.new_map_points[i]
			for j in range(0, len(self.new_map_edges[i])):
				point2 = self.new_map_points[self.new_map_edges[i][j]]
				self.map_graph.add_edge(point1, point2, point1.distance_to(point2))

		# Bases
		self.base_main = self.convert_location((143.5, 32.5))
		self.base_natural = self.convert_location((145.5, 61.5)) 
		base_natural_edge = 44
		self.map_graph.add_edge(self.base_natural, self.new_map_points[base_natural_edge], self.base_natural.distance_to(self.new_map_points[base_natural_edge]))
		self.map_graph.add_edge(self.new_map_points[base_natural_edge], self.base_natural, self.base_natural.distance_to(self.new_map_points[base_natural_edge]))
		
		self.bases_left = [self.convert_location((119.5, 53.5)),
								self.convert_location((104.5, 27.5))]
		bases_left_edges = [[3, 12, 35, 40],
							[17, 37]]
		for i in range(0, len(bases_left_edges)):
			point1 = self.bases_left[i]
			for j in range(0, len(bases_left_edges[i])):
				point2 = self.new_map_points[bases_left_edges[i][j]]
				self.map_graph.add_edge(point1, point2, point1.distance_to(point2))
				self.map_graph.add_edge(point2, point1, point1.distance_to(point2))

		self.bases_right = [self.convert_location((147.5, 94.5)),
									self.convert_location((148.5, 125.5)),
									self.convert_location((124.5, 120.5))]
		bases_right_edges = [[13, 46],
							[20, 22],
							[16, 19, 21, 34]]
		for i in range(0, len(bases_right_edges)):
			point1 = self.bases_right[i]
			for j in range(0, len(bases_right_edges[i])):
				point2 = self.new_map_points[bases_right_edges[i][j]]
				self.map_graph.add_edge(point1, point2, point1.distance_to(point2))
				self.map_graph.add_edge(point2, point1, point1.distance_to(point2))

		

		self.enemy_base_main = self.convert_location((40.5, 131.5))
		self.enemy_base_natural = self.convert_location((38.5, 102.5))
		enemy_base_natural_edge = 93
		self.map_graph.add_edge(self.enemy_base_natural, self.new_map_points[enemy_base_natural_edge], self.enemy_base_natural.distance_to(self.new_map_points[enemy_base_natural_edge]))
		self.map_graph.add_edge(self.new_map_points[enemy_base_natural_edge], self.enemy_base_natural, self.enemy_base_natural.distance_to(self.new_map_points[enemy_base_natural_edge]))
		
		self.enemy_bases_left = [self.convert_location((64.5, 110.5)),
							self.convert_location((79.5, 136.5))]
		enemy_bases_left_edges = [	[52, 61, 84, 89],
									[66, 86]]
		for i in range(0, len(enemy_bases_left_edges)):
			point1 = self.enemy_bases_left[i]
			for j in range(0, len(enemy_bases_left_edges[i])):
				point2 = self.new_map_points[enemy_bases_left_edges[i][j]]
				self.map_graph.add_edge(point1, point2, point1.distance_to(point2))
				self.map_graph.add_edge(point2, point1, point1.distance_to(point2))
		self.enemy_bases_right = [self.convert_location((36.5, 69.5)),
							self.convert_location((35.5, 38.5)),
							self.convert_location((59.5, 43.5))]
		enemy_bases_right_edges = [	[62, 95],
									[69, 71],
									[65, 68, 70, 83]]
		for i in range(0, len(enemy_bases_right_edges)):
			point1 = self.enemy_bases_right[i]
			for j in range(0, len(enemy_bases_right_edges[i])):
				point2 = self.new_map_points[enemy_bases_right_edges[i][j]]
				self.map_graph.add_edge(point1, point2, point1.distance_to(point2))
				self.map_graph.add_edge(point2, point1, point1.distance_to(point2))
		

		self.bases = [self.base_main, self.base_natural] + self.bases_left + self.bases_right
		self.enemy_bases = [self.enemy_base_main, self.enemy_base_natural] + self.enemy_bases_left + self.enemy_bases_right

		


		# Army
		
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
		
		
		self.rally_points_left = [self.convert_location((84, 117)),
									self.convert_location((93, 123)),
									self.convert_location((114, 131))]
		self.rally_points_right = [self.convert_location((40, 70)),
									self.convert_location((60, 46)),
									self.convert_location((87, 33)),
									self.convert_location((65, 27))]
		
		
		
		self.ling_runby_left_rally = self.convert_location((129, 141))
		self.ling_runby_right_rally = self.convert_location((55, 23))

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
		# attack l/r, base l/r, drop l/r
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
		
