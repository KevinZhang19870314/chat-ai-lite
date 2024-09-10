from typing import Any, List, Union, Callable, Optional
from inspect import signature

from langchain.tools import BaseTool
from langchain.agents import Tool
from pydantic import ConfigDict, Field


# All @tool decorated functions in plugins become a BotTool.
# The difference between base langchain Tool and BotTool is that BotTool has an instance of the bot as attribute (set by the MadHatter)
class BotTool(Tool):
	bot: Any = Field()
	plugin_id: Any = Field()
	docstring: str = Field()
	doc_id: Any = Field()

	# def __init__(self, name: str, func: Optional[Callable], description: str, plugin_id: Any, **kwargs: Any):
	# 	super().__init__(name, func, description, **kwargs)
	# 	self.plugin_id = plugin_id

	# used by the MadHatter while loading plugins in order to let a Tool access the bot instance
	def augment_tool(self, bot_instance):
		self.bot = bot_instance

		# Tool docstring, is also available under self.func.__doc__
		self.docstring = self.func.__doc__

		# remove bot argument from description signature
		# so it does not end up in prompts
		bot_arg_signature = ", bot)"
		if bot_arg_signature in self.description:
			self.description = self.description.replace(bot_arg_signature, ")")

		# Tool doc_id is saved in the "procedural" vector DB collection.
		# During DeepAI.bootstrap(), after memory is loaded, the mad_hatter will retrieve the doc_id from memory or create one if not present, and assign this attribute
		self.doc_id = None

	def _run(self, input_by_llm):
		return self.func(input_by_llm, bot=self.bot)

	async def _arun(self, input_by_llm):
		# should be used for async Tools, just using sync here
		return self._run(input_by_llm, bot=self.bot)
	model_config = ConfigDict(extra="allow")


# @tool decorator, a modified version of a langchain Tool that also takes a bot instance as argument
# adapted from https://github.com/hwchase17/langchain/blob/master/langchain/agents/tools.py
def tool(*args: Union[str, Callable], return_direct: bool = False) -> Callable:
	"""Make tools out of functions, can be used with or without arguments.
	Requires:
			- Function must be of type (str) -> str
			- Function must have a docstring
	Examples:
			.. code-block:: python
					@tool
					def search_api(query: str) -> str:
							# Searches the API for the query.
							return
					@tool("search", return_direct=True)
					def search_api(query: str) -> str:
							# Searches the API for the query.
							return
	"""

	def _make_with_name(tool_name: str) -> Callable:
		def _make_tool(func: Callable[[str], str]) -> Tool:
			assert func.__doc__, "Function must have a docstring"
			# Description example:
			#   search_api(query: str) - Searches the API for the query.
			description = f"{tool_name}{signature(func)} - {func.__doc__.strip()}"
			tool_ = BotTool(
				name=tool_name,
				func=func,
				description=description,
				return_direct=return_direct,
			)
			return tool_

		return _make_tool

	if len(args) == 1 and isinstance(args[0], str):
		# if the argument is a string, then we use the string as the tool name
		# Example usage: @tool("search", return_direct=True)
		return _make_with_name(args[0])
	elif len(args) == 1 and callable(args[0]):
		# if the argument is a function, then we use the function name as the tool name
		# Example usage: @tool
		return _make_with_name(args[0].__name__)(args[0])
	elif len(args) == 0:
		# if there are no arguments, then we use the function name as the tool name
		# Example usage: @tool(return_direct=True)
		def _partial(func: Callable[[str], str]) -> BaseTool:
			return _make_with_name(func.__name__)(func)

		return _partial
	else:
		raise ValueError("Too many arguments for tool decorator")
