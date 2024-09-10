from pydantic import BaseModel

from mad_hatter.decorators import hook


# this class represents settings for the core plugin (at the moment empty)
class CorePluginSettings(BaseModel):
	pass
	#    length: int  # required field, type int
	#    description: str = "my fav cat" # optional field, type str, with a default


@hook(priority=0)
def plugin_settings_schema():
	"""
	This hook tells the cat how plugin settings are defined, required vs optional, default values, etc.
	The standard used is JSON SCHEMA, so a client can auto-generate html forms (see https://json-schema.org/ ).

	Schema can be created in several ways:
	1. auto-generarted with pydantic (see below)
	2. python dictionary
	3. json loaded from current folder or from another place

	Default behavior for this hook is defined in:
		 `cat.mad_hatter.plugin.Plugin::get_settings_schema`

	Returns
	-------
	schema : Dict
			JSON schema of the settings.
	"""

	# In core_plugin we pass an empty JSON schema
	return CorePluginSettings.schema()


@hook(priority=0)
def plugin_settings_load():
	"""
	This hook defines how to load saved settings for the plugin.

	Default behavior for this hook is defined in:
		 `cat.mad_hatter.plugin.Plugin::load_settings`
		 It loads the settings.json in current folder

	Returns
	-------
	settings : Dict
			Settings.
	"""

	# In core_plugin we do nothing (for now).
	return {}


@hook(priority=0)
def plugin_settings_save(settings):
	"""
	This hook passes the plugin settings as sent to the http endpoint (via admin, or any client), in order to let the plugin save them as desired.
	The settings to save should be validated according to the json schema given in the `plugin_settings_schema` hook.

	Default behavior for this hook is defined in:
		 `cat.mad_hatter.plugin.Plugin::save_settings`
		 It just saves contents in a settings.json in the plugin folder

	Parameters
	----------
	settings : Dict
			Settings to be saved.

	Returns
	-------
	settings : Dict
			Saved settings.
	"""

	# In core_plugin we do nothing (for now).
	return {}
