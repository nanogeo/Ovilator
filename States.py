from __future__ import annotations
from FSM import State, StateMachine
import Enums
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ZergBot import ZergBot


class BlankState(State):

	def tick_state(self):
		pass

	def enter_state(self):
		pass

	def exit_state(self):
		pass

	# return new state or None
	def test_transitions(self):
		pass



########## Army ##########

class ArmyStateMachine(StateMachine):
	def __init__(self, bot: ZergBot):
		super().__init__(bot, ArmyStateConsolidating(bot))

class ArmyStateConsolidating(State):
	def __init__(self, bot: ZergBot):
		super().__init__(bot)

	def tick_state(self):
		# get enemy army state
		enemy_army_state = self.bot.enemy_army_state
		move_points = (None, None)
		if enemy_army_state == Enums.EnemyArmyState.DEFENDING:
			# if enemy is defending then get consolidation points
			move_points = self.bot.get_consolidation_points()
		else:
			# if enemy isnt then get flank positions
			move_points = self.bot.get_flank_points()

		# move to correct positions
		self.bot.move_units(self.bot.units.tags_in(self.bot.main_army_left), move_points[0])
		self.bot.move_units(self.bot.units.tags_in(self.bot.main_army_right), move_points[1])


	def enter_state(self):
		pass

	def exit_state(self):
		pass

	# return new state or None
	def test_transitions(self):
		# if under attack, protect
		defense_point = self.bot.need_to_protect()
		if defense_point:
			return ArmyStateProtecting(self.bot, defense_point)
		# if enough supply, rally
		if self.bot.supply_army >= 100:
			return ArmyStateRallying(self.bot, self.bot.time)
		return None
		
	def __str__(self):
		return "Consolidating"


class ArmyStateRallying(State):

	def __init__(self, bot: ZergBot, time):
		super().__init__(bot)
		self.start_time = time

	def tick_state(self):
		# move each unit to the rally point
		self.bot.move_army_to_next_point()

	def enter_state(self):
		# set rally point and attack targets for all units
		left_targets = self.bot.get_targets_left()
		right_targets = self.bot.get_targets_right()
		for info in self.bot.main_army_left_info.values():
			info.targets = left_targets.copy()
		for info in self.bot.main_army_right_info.values():
			info.targets = right_targets.copy()
		

	def exit_state(self):
		# remove rally point from targets list
		for info in self.bot.main_army_left_info.values():
			info.targets.pop(0)
		for info in self.bot.main_army_right_info.values():
			info.targets.pop(0)

	# return new state or None
	def test_transitions(self):
		# if we've been rallying for 20 sec, attack
		if self.bot.time > self.start_time + 20:
			return ArmyStateAttacking(self.bot)
		# if everyone is in pos, attack
		if self.bot.all_units_at_target():
			return ArmyStateAttacking(self.bot)
		# if under attack, protect
		defense_point = self.bot.need_to_protect()
		if defense_point:
			return ArmyStateProtecting(self.bot, defense_point)
		return None
		
	def __str__(self):
		return "Rallying"

class ArmyStateProtecting(State):

	def __init__(self, bot: ZergBot, defense_point):
		super().__init__(bot)
		self.defense_point = defense_point

	def tick_state(self):
		# micro units toward protection point
		self.bot.army_attack_next_point()

	def enter_state(self):
		for info in self.bot.main_army_left_info.values():
			info.targets = [self.defense_point]
		for info in self.bot.main_army_right_info.values():
			info.targets = [self.defense_point]

	def exit_state(self):
		for info in self.bot.main_army_left_info.values():
			info.targets = []
		for info in self.bot.main_army_right_info.values():
			info.targets = []

	# return new state or None
	def test_transitions(self):
		# if under no longer under attack, consolidate
		if not self.bot.need_to_protect():
			return ArmyStateConsolidating(self.bot)
		
		return None
		
	def __str__(self):
		return "Protecting"

class ArmyStateAttacking(State):
	def __init__(self, bot: ZergBot):
		super().__init__(bot)

	def tick_state(self):
		self.bot.update_targets()
		# if we have 2x army supply then add new units to army groups

		# micro units toward attack points
		self.bot.update_targets()
		self.bot.army_attack_next_point()

	def enter_state(self):
		pass

	def exit_state(self):
		pass

	# return new state or None
	def test_transitions(self):
		# if all army units dead, consolidate
		if len(self.bot.units.tags_in(self.bot.main_army_left + self.bot.main_army_right)) == 0:
			return ArmyStateConsolidating(self.bot)
		return None
		
	def __str__(self):
		return "Attacking"