import traceback

from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, LLMSingleActionAgent
from langchain.chains import LLMChain

from log import log
from looking_glass.output_parser import ToolOutputParser
from looking_glass.prompts import ToolPromptTemplate
from utils import config_metadata_chain


class AgentManager:
	def __init__(self, bot):
		self.bot = bot

	def execute_tool_agent(self, agent_input, allowed_tools):
		allowed_tools_names = [t.name for t in allowed_tools]

		prompt = ToolPromptTemplate(
			template=self.bot.mad_hatter.execute_hook("agent_prompt_instructions"),
			tools=allowed_tools,
			# This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
			# This includes the `intermediate_steps` variable because it is needed to fill the scratchpad
			input_variables=["input", "intermediate_steps"]
		)

		# main chain
		agent_chain = LLMChain(prompt=prompt, llm=self.bot.llm, verbose=True)

		# init agent
		agent = LLMSingleActionAgent(
			llm_chain=agent_chain,
			output_parser=ToolOutputParser(),
			stop=["\nObservation:"],
			allowed_tools=allowed_tools_names,
			verbose=True
		)

		# agent executor
		agent_executor = AgentExecutor.from_agent_and_tools(
			agent=agent,
			tools=allowed_tools,
			return_intermediate_steps=True,
			verbose=True
		)

		agent_executor: AgentExecutor = config_metadata_chain(agent_executor, {"email": self.bot.email})

		out = agent_executor.invoke(agent_input)
		return out

	def execute_memory_chain(self, agent_input, prompt_prefix, prompt_suffix):
		# memory chain (second step)
		memory_prompt = PromptTemplate(
			template=prompt_prefix + prompt_suffix,
			input_variables=[
				"input",
				"chat_history",
				"declarative_memory",
				"tools_output"
			]
		)

		memory_chain = LLMChain(
			prompt=memory_prompt,
			llm=self.bot.llm,
			verbose=True
		)

		memory_chain = config_metadata_chain(memory_chain, {"email": self.bot.email})

		out = memory_chain.invoke(agent_input)
		out["output"] = out["text"]
		del out["text"]
		return out

	def execute_memory_chain_stream(self, agent_input, prompt_prefix, prompt_suffix):
		# memory chain (second step)
		memory_prompt = PromptTemplate(
			template=prompt_prefix + prompt_suffix,
			input_variables=[
				"input",
				"chat_history",
				"declarative_memory",
				"tools_output"
			]
		)

		memory_chain = memory_prompt | self.bot.llm

		memory_chain = config_metadata_chain(memory_chain, {"email": self.bot.email})

		interator = memory_chain.stream(agent_input)
		return interator

	def execute_agent(self, agent_input):
		mad_hatter = self.bot.mad_hatter

		# this hook allows to reply without executing the agent (for example canned responses, out-of-topic barriers etc.)
		fast_reply = mad_hatter.execute_hook("before_agent_starts", agent_input)
		if fast_reply:
			return fast_reply

		prompt_prefix = mad_hatter.execute_hook("agent_prompt_prefix")
		prompt_suffix = mad_hatter.execute_hook("agent_prompt_suffix")

		# Try to reply only with tools
		allowed_tools = mad_hatter.execute_hook("agent_allowed_tools")

		# Try to get information from tools if there is some allowed
		if len(allowed_tools) > 0:

			log(f"{len(allowed_tools)} allowed tools retrieved.", "DEBUG")

			try:
				tools_result = self.execute_tool_agent(agent_input, allowed_tools)

				# If tools_result["output"] is None the LLM has used the fake tool none_of_the_others
				# so no relevant information has been obtained from the tools.
				if tools_result["output"] is not None:

					# Extract of intermediate steps in the format ((tool_name, tool_input), output)
					used_tools = list(map(lambda x: ((x[0].tool, x[0].tool_input), x[1]), tools_result["intermediate_steps"]))

					# Get the name of the tools that have return_direct
					return_direct_tools = []
					for t in allowed_tools:
						if t.return_direct:
							return_direct_tools.append(t.name)

					# execute_tool_agent returns immediately when a tool with return_direct is called,
					# so if one is used it is definitely the last one used
					if used_tools[-1][0][0] in return_direct_tools:
						# intermediate_steps still contains the information of all the tools used even if their output is not returned
						tools_result["intermediate_steps"] = used_tools
						return tools_result

					# Adding the tools_output key in agent input, needed by the memory chain
					agent_input["tools_output"] = "## Tools output: \n" + tools_result["output"] if tools_result["output"] else ""

					# Execute the memory chain
					out = self.execute_memory_chain(agent_input, prompt_prefix, prompt_suffix)

					# If some tools are used the intermediate step are added to the agent output
					out["intermediate_steps"] = used_tools

					# Early return
					return out

			except Exception as e:
				traceback.print_exc()
				error_description = str(e)
				log(error_description, "ERROR")

		# If an exception occur in the execute_tool_agent or there is no allowed tools execute only the memory chain

		# Adding the tools_output key in agent input, needed by the memory chain
		agent_input["tools_output"] = ""
		# Execute the memory chain
		out = self.execute_memory_chain(agent_input, prompt_prefix, prompt_suffix)

		return out

	def execute_agent_stream(self, agent_input):
		mad_hatter = self.bot.mad_hatter

		# this hook allows to reply without executing the agent (for example canned responses, out-of-topic barriers etc.)
		fast_reply = mad_hatter.execute_hook("before_agent_starts", agent_input)
		if fast_reply:
			return fast_reply

		prompt_prefix = mad_hatter.execute_hook("agent_prompt_prefix")
		prompt_suffix = mad_hatter.execute_hook("agent_prompt_suffix")

		# Try to reply only with tools
		allowed_tools = mad_hatter.execute_hook("agent_allowed_tools")

		# Try to get information from tools if there is some allowed
		if len(allowed_tools) > 0:

			log(f"{len(allowed_tools)} allowed tools retrieved.", "DEBUG")

			try:
				tools_result = self.execute_tool_agent(agent_input, allowed_tools)

				# If tools_result["output"] is None the LLM has used the fake tool none_of_the_others
				# so no relevant information has been obtained from the tools.
				if tools_result["output"] is not None:

					# Extract of intermediate steps in the format ((tool_name, tool_input), output)
					used_tools = list(map(lambda x: ((x[0].tool, x[0].tool_input), x[1]), tools_result["intermediate_steps"]))

					# Get the name of the tools that have return_direct
					return_direct_tools = []
					for t in allowed_tools:
						if t.return_direct:
							return_direct_tools.append(t.name)

					# execute_tool_agent returns immediately when a tool with return_direct is called,
					# so if one is used it is definitely the last one used
					if used_tools[-1][0][0] in return_direct_tools:
						# intermediate_steps still contains the information of all the tools used even if their output is not returned
						tools_result["intermediate_steps"] = used_tools
						return tools_result

					# Adding the tools_output key in agent input, needed by the memory chain
					agent_input["tools_output"] = "## Tools output: \n" + tools_result["output"] if tools_result["output"] else ""

					# Execute the memory chain
					interator = self.execute_memory_chain_stream(agent_input, prompt_prefix, prompt_suffix)

					# Early return
					return interator

			except Exception as e:
				error_description = str(e)
				log(error_description, "ERROR")

		# If an exception occur in the execute_tool_agent or there is no allowed tools execute only the memory chain

		# Adding the tools_output key in agent input, needed by the memory chain
		agent_input["tools_output"] = ""
		# Execute the memory chain
		interator = self.execute_memory_chain_stream(agent_input, prompt_prefix, prompt_suffix)

		return interator
