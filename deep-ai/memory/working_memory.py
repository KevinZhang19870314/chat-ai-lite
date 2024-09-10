class WorkingMemory(dict):
	"""Handy class that behaves like a `dict` to store custom data."""

	def __init__(self):
		# The constructor instantiates a `dict` with a 'history' key to store conversation history
		super().__init__(history=[])

	def update_conversation_history(self, session_id, who, message):
		self["history"].append({"session_id": session_id, "who": who, "message": message})

	def get_conversation_history(self, session_id):
		user_history = [h for h in self["history"] if h["session_id"] == session_id] if session_id is not None else []
		return user_history

	def delete_conversation_history(self, session_id):
		self["history"] = [h for h in self["history"] if h["session_id"] != session_id] if session_id is not None else self["history"]

