

class State:

	def __init__(self, bot):
		self.bot = bot

	def tick_state(self):
		print("Error tick_state call on State base class")

	def enter_state(self):
		print("Error enter_state call on State base class")

	def exit_state(self):
		print("Error exit_state call on State base class")

	def test_transitions(self):
		print("Error test_transitions call on State base class")

	def __str__(self):
		return "State"

class StateMachine:
	

	def __init__(self, bot, default_state):
		self.bot = bot
		self.current_state = default_state
		
	def run_state_machine(self):
		new_state = self.current_state.test_transitions()
		if new_state != None:
			self.current_state.exit_state()
			self.current_state = new_state
			self.current_state.enter_state()
		self.current_state.tick_state()

	def get_state(self):
		return str(self.current_state)