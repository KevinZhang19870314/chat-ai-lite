import importlib
import os
import json
import glob
import sys
import traceback
from typing import Dict
from inspect import getmembers

from pydantic import BaseModel
from mad_hatter.decorators import BotHook, BotTool
from utils import to_camel_case
from log import log, get_log_level
from importlib.machinery import SourceFileLoader


# this class represents a plugin in memory
# the plugin itself is managed as much as possible unix style
#      (i.e. by saving information in the folder itself)


class Plugin:

	def __init__(self, plugin_path, active: bool):
		# does folder exist?
		if not os.path.exists(plugin_path) or not os.path.isdir(plugin_path):
			raise Exception(f"{plugin_path} does not exist or is not a folder. Cannot create Plugin.")

		# where the plugin is on disk
		self._path: str = plugin_path

		# search for .py files in folder
		py_files_path = os.path.join(self._path, "**/*.py")
		self.py_files = glob.glob(py_files_path, recursive=True)

		if len(self.py_files) == 0:
			raise Exception(f"{plugin_path} does not contain any python files. Cannot create Plugin.")

		# plugin id is just the folder name
		self._id: str = os.path.basename(os.path.normpath(plugin_path))

		# plugin manifest (name, decription, thumb, etc.)
		self._manifest = self._load_manifest()

		self._hooks = []
		self._tools = []

		self._active = False

		# all plugins start active, they can be deactivated/reactivated from endpoint
		if active:
			self.activate()

	def activate(self):
		# lists of hooks and tools
		self._hooks, self._tools = self._load_hooks_and_tools()
		self._active = True

	def deactivate(self):
		self._active = False

		# Remove the imported modules
		for py_file in self.py_files:
			py_filename = py_file.replace("/", ".").replace("\\", ".").replace(".py", "")		# this is UGLY I know. I'm sorry
			# If the module is imported it is removed
			if py_filename in sys.modules:
				log(f"Remove module {py_filename}", "DEBUG")
				sys.modules.pop(py_filename)

		self._hooks = []
		self._tools = []

	# get plugin settings JSON schema
	def get_settings_schema(self):

		# is "plugin_settings_schema" hook defined in the plugin?
		for h in self._hooks:
			if h.name == "plugin_settings_schema":
				return h.function()

		# default schema (empty)
		return BaseModel.schema()

	# load plugin settings
	def load_settings(self):

		# is "plugin_settings_load" hook defined in the plugin?
		for h in self._hooks:
			if h.name == "plugin_settings_load":
				return h.function()

		# by default, plugin settings are saved inside the plugin folder
		#   in a JSON file called settings.json
		settings_file_path = os.path.join(self._path, "settings.json")

		# default settings is an empty dictionary
		settings = {}

		# load settings.json if exists
		if os.path.isfile(settings_file_path):
			try:
				with open(settings_file_path, "r") as json_file:
					settings = json.load(json_file)
			except Exception as e:
				log(f"Unable to load plugin {self._id} settings", "ERROR")
				log(e, "ERROR")

		return settings

	# save plugin settings
	def save_settings(self, settings: Dict):

		# is "plugin_settings_save" hook defined in the plugin?
		for h in self._hooks:
			if h.name == "plugin_settings_save":
				return h.function(settings)

		# by default, plugin settings are saved inside the plugin folder
		#   in a JSON file called settings.json
		settings_file_path = os.path.join(self._path, "settings.json")

		# load already saved settings
		old_settings = self.load_settings()

		# overwrite settings over old ones
		updated_settings = {**old_settings, **settings}

		# write settings.json in plugin folder
		try:
			with open(settings_file_path, "w") as json_file:
				json.dump(updated_settings, json_file, indent=4)
		except Exception:
			log(f"Unable to save plugin {self._id} settings", "ERROR")
			return {}

		return updated_settings

	# load contents of plugin.json (if exists)
	def _load_manifest(self):
		plugin_json_metadata_file_name = "plugin.json"
		plugin_json_metadata_file_path = os.path.join(self._path, plugin_json_metadata_file_name)
		meta = {"id": self._id}
		json_file_data = {}

		if os.path.isfile(plugin_json_metadata_file_path):
			try:
				json_file = open(plugin_json_metadata_file_path, encoding='utf-8')
				json_file_data = json.load(json_file)
				json_file.close()
			except Exception as e:
				print(str(e))
				log(f"Loading plugin {self._path} metadata, defaulting to generated values", "INFO")

		meta["name"] = json_file_data.get("name", to_camel_case(self._id))
		meta["description"] = json_file_data.get("description", (
			"Description not found for this plugin. "
			f"Please create a `{plugin_json_metadata_file_name}`"
			" in the plugin folder."
		))
		meta["author_name"] = json_file_data.get("author_name", "Unknown author")
		meta["author_url"] = json_file_data.get("author_url", "")
		meta["plugin_url"] = json_file_data.get("plugin_url", "")
		meta["tags"] = json_file_data.get("tags", "unknown")
		meta["thumb"] = json_file_data.get("thumb", "")
		meta["version"] = json_file_data.get("version", "0.0.1")

		return meta

	# lists of hooks and tools
	def _load_hooks_and_tools(self):
		hooks = []
		tools = []

		for py_file in self.py_files:
			py_filename = py_file.replace("/", ".").replace("\\", ".").replace(".py", "")  # this is UGLY I know. I'm sorry

			log(f"Import module {py_filename}", "DEBUG")

			# save a reference to decorated functions
			try:
				plugin_module = importlib.import_module(py_filename)
				# plugin_module = SourceFileLoader(f'{py_filename}', py_filename).load_module()
				hooks += getmembers(plugin_module, self._is_bot_hook)
				tools += getmembers(plugin_module, self._is_bot_tool)
			except Exception as e:
				log(f"Error in {py_filename}: {str(e)}", "ERROR")
				if get_log_level() == "DEBUG":
					traceback.print_exc()
				raise Exception(f"Unable to load the plugin {self._id}")

		# clean and enrich instances
		hooks = list(map(self._clean_hook, hooks))
		tools = list(map(self._clean_tool, tools))

		return hooks, tools

	def _clean_hook(self, hook):
		# getmembers returns a tuple
		h = hook[1]
		h.plugin_id = self._id
		return h

	def _clean_tool(self, tool):
		# getmembers returns a tuple
		t = tool[1]
		t.plugin_id = self._id
		return t

	# a plugin hook function has to be decorated with @hook
	# (which returns an instance of BotHook)
	@staticmethod
	def _is_bot_hook(obj):
		return isinstance(obj, BotHook)

	# a plugin tool function has to be decorated with @tool
	# (which returns an instance of BotTool)
	@staticmethod
	def _is_bot_tool(obj):
		return isinstance(obj, BotTool)

	@property
	def path(self):
		return self._path

	@property
	def id(self):
		return self._id

	@property
	def active(self):
		return self._active

	@property
	def manifest(self):
		return self._manifest

	@property
	def hooks(self):
		return self._hooks

	@property
	def tools(self):
		return self._tools
