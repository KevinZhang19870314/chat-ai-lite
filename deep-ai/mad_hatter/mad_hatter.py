import glob
import os
import shutil
import time
import traceback

from langchain_community.vectorstores.faiss import FAISS

from db import crud_activeplugin, crud_knowledgebase
from infrastructure.package import Package
from install_plugin_dependencies import install_plugin_dependencies
from log import log
from mad_hatter.plugin import Plugin


# This class is responsible for plugins functionality:
# - loading
# - prioritizing
# - executing
class MadHatter:
	# loads and execute plugins
	# - enter into the plugin folder and loads everything
	#   that is decorated or named properly
	# - orders plugged in hooks by name and priority
	# - exposes functionality to the bot

	def __init__(self, bot):
		self.bot = bot

		self.plugins = {}  # plugins dictionary

		# global plugins
		self.hooks = []  # list of active plugins hooks
		self.tools = []  # list of active plugins tools
		self.active_plugins = []

		# plugins per knowledge base
		self.use_plugins = []

		self.find_plugins()

	def install_plugin(self, package_plugin):

		# extract zip/tar file into plugin folder
		plugin_folder = self.bot.get_plugin_path()
		# check plugin_folder exists, if not, mkdir it
		if not os.path.isdir(plugin_folder):
			os.mkdir(plugin_folder)
		archive = Package(package_plugin)
		extracted_contents = archive.unpackage(plugin_folder)

		# there should be a method to check for plugin integrity
		if len(extracted_contents) != 1:
			raise Exception("A plugin should consist in one new folder: "
											"found many contents in compressed archive or plugin already present.")

		plugin_id = extracted_contents[0]
		plugin_path = os.path.join(plugin_folder, plugin_id)

		if not os.path.isdir(plugin_path):
			raise Exception("A plugin should contain a folder, found a file")

		install_plugin_dependencies(plugin_path)

		# create plugin obj
		self.load_plugin(plugin_path, active=False)

		# activate it
		self.toggle_plugin(plugin_id)

	def uninstall_plugin(self, plugin_id):

		if self.plugin_exists(plugin_id):
			# deactivate plugin if it is active (will sync cache)
			if plugin_id in self.active_plugins:
				self.toggle_plugin(plugin_id)

			# remove plugin from cache
			plugin_path = self.plugins[plugin_id].path
			del self.plugins[plugin_id]

			# remove plugin folder
			shutil.rmtree(plugin_path)

	def find_plugins(self):

		# plugins will be discovered from disk
		#   and stored in a dictionary plugin_id -> plugin_obj
		self.plugins = {}

		self.active_plugins = self.load_active_plugins_from_db()

		# plugins are found in the plugins folder,
		#   plus the default core plugin (where default hooks and tools are defined)
		core_plugin_folder = "mad_hatter/core_plugin/"
		# plugin folder is "plugins/" in production
		plugin_folder = self.bot.get_plugin_path()
		all_plugin_folders = [core_plugin_folder] + glob.glob(f"{plugin_folder}*/")

		log("ACTIVE PLUGINS:", "INFO")
		log(self.active_plugins, "INFO")

		# discover plugins, folder by folder
		for folder in all_plugin_folders:
			folder_base = os.path.basename(os.path.normpath(folder))
			is_active = folder_base in self.active_plugins
			install_plugin_dependencies(folder)
			self.load_plugin(folder, is_active)

		self.sync_hooks_and_tools()

	def load_plugin(self, plugin_path, active):
		# Instantiate plugin.
		try:
			plugin = Plugin(plugin_path, active=active)
			# if plugin is valid, keep a reference
			self.plugins[plugin.id] = plugin
		except Exception as e:
			traceback.print_exc()
			log(str(e), "ERROR")

	def sync_hooks_and_tools(self, filter_plugins=None):
		if filter_plugins is None:
			filter_plugins = self.active_plugins

		# emptying tools and hooks
		self.hooks = []
		self.tools = []

		for _, plugin in self.plugins.items():
			if plugin.id in filter_plugins:
				for t in plugin.tools:
					# Prepare the tool to be used in the Bot (setting the bot instance, adding properties)
					t.augment_tool(self.bot)

				self.hooks += plugin.hooks
				self.tools += plugin.tools

		# sort hooks by priority
		self.hooks.sort(key=lambda x: x.priority, reverse=True)

	def get_use_plugins(self, knowledge_base_id):
		use_plugins = crud_knowledgebase.get_use_plugins_by_id(next(self.bot.db()), knowledge_base_id)
		set_active_plugins = set(self.active_plugins)
		set_use_plugins = set(use_plugins)
		use_plugins = list(set_active_plugins.intersection(set_use_plugins))

		# core_plugin is always active
		if "core_plugin" not in use_plugins:
			use_plugins += ["core_plugin"]

		return use_plugins

	def sync_hooks_and_tools_when_chat(self, knowledge_base_id):
		self.use_plugins = self.get_use_plugins(knowledge_base_id)

		if len(self.use_plugins) == 0:
			return

		self.sync_hooks_and_tools(self.use_plugins)

	# check if plugin exists
	def plugin_exists(self, plugin_id):
		return plugin_id in self.plugins.keys()

	def load_active_plugins_from_db(self):
		records = crud_activeplugin.get_all_active_plugins(next(self.bot.db()))

		if records is None:
			active_plugins = []
		else:
			active_plugins = [record.name for record in records]

		# core_plugin is always active
		if "core_plugin" not in active_plugins:
			active_plugins += ["core_plugin"]

		return active_plugins

	def save_active_plugins_to_db(self, active_plugins):
		crud_activeplugin.bulk_insert_active_plugins(next(self.bot.db()), active_plugins)

	# loops over tools and assign an doc_id each. If an doc_id is not present in vectorDB, it is created and saved
	def embed_tools(self):
		index_name = "procedural"

		# retrieve from vectorDB all tool embeddings
		vector_db: FAISS = self.bot.memory.vectors.faiss_db(index_name)
		tools_in_vector_db = vector_db.docstore.__dict__['_dict']

		# easy access to plugin tools
		plugins_tools_index = {t.description: t for t in self.tools}

		ids_to_be_deleted = []

		# loop over vectors
		for doc_id in tools_in_vector_db:
			# if the tools is active in plugins, assign doc_id
			try:
				tool_description = tools_in_vector_db[doc_id].page_content
				plugins_tools_index[tool_description].doc_id = doc_id
			# else delete it
			except Exception as e:
				log(f"Deleting embedded tool: {doc_id} - {tools_in_vector_db[doc_id].page_content}", "WARNING")
				ids_to_be_deleted.append(doc_id)

		if len(ids_to_be_deleted) > 0:
			# vector_db.delete(ids=ids_to_be_deleted)
			log(f"Ids to be deleted: {ids_to_be_deleted}")
			vector_db = self.bot.memory.vectors.remove(index_name, ids_to_be_deleted)

		# loop over tools
		for tool in self.tools:
			# if there is no doc_id, create it
			if not tool.doc_id:
				# save it to DB
				ids_inserted = vector_db.add_texts(
					[tool.description],
					[{
						"source": "tool",
						"when": time.time(),
						"name": tool.name,
						"docstring": tool.docstring
					}],
				)

				tool.doc_id = ids_inserted[0]
				log(f"Newly embedded tool: {tool.doc_id} - {tool.description}", "WARNING")
		# save to local
		vector_db.save_local(self.bot.common_storage, index_name)

	# activate / deactivate plugin
	def toggle_plugin(self, plugin_id):
		if self.plugin_exists(plugin_id):

			plugin_is_active = plugin_id in self.active_plugins

			# update list of active plugins
			if plugin_is_active:
				log(f"Toggle plugin {plugin_id}: Deactivate", "WARNING")
				# Deactivate the plugin
				self.plugins[plugin_id].deactivate()
				# Remove the plugin from the list of active plugins
				self.active_plugins.remove(plugin_id)
			else:
				log(f"Toggle plugin {plugin_id}: Activate", "WARNING")
				# Activate the plugin
				self.plugins[plugin_id].activate()
				# Ass the plugin in the list of active plugins
				self.active_plugins.append(plugin_id)

			# update DB with list of active plugins, delete duplicate plugins
			self.save_active_plugins_to_db(list(set(self.active_plugins)))

			# update cache and embeddings
			self.sync_hooks_and_tools()
			self.embed_tools()

		else:
			raise Exception("Plugin {plugin_id} not present in plugins folder")

	# execute requested hook
	def execute_hook(self, hook_name, *args):
		for h in self.hooks:
			if hook_name == h.name:
				return h.function(*args, bot=self.bot)

		# every hook must have a default in core_plugin
		raise Exception(f"Hook {hook_name} not present in any plugin")
