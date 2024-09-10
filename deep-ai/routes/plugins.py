import mimetypes
from copy import deepcopy
from tempfile import NamedTemporaryFile
from typing import Dict
from urllib.parse import urlparse

import requests
from fastapi import Request, APIRouter, UploadFile, BackgroundTasks, HTTPException, Body, Response

from log import log
from response import ApiResponse, Status
from routes.helper import get_bot

router = APIRouter()


def get_registry_list():
	try:
		response = requests.get("https://plugins.deep.ai/plugins?page=1&page_size=7000")
		if response.status_code == 200:
			return response.json()["plugins"]
		else:
			return []
	except requests.exceptions.RequestException:
		return []


# GET all active/inactive plugins
@router.get("/all")
async def get_available_plugins(request: Request):
	"""List available plugins"""
	try:
		bot = get_bot(request.app.state.bot)

		active_plugins = bot.mad_hatter.load_active_plugins_from_db()

		# plugins are managed by the MadHatter class
		plugins = []
		log(f"PLUGINS: {bot.mad_hatter.plugins.values()}")
		for p in bot.mad_hatter.plugins.values():
			manifest = deepcopy(p.manifest)  # we make a copy to avoid modifying the plugin obj
			manifest["active"] = p.id in active_plugins  # pass along if plugin is active or not
			plugins.append(manifest)

		# retrieve plugins from official repo
		registry = get_registry_list()

		data = {
			"installed": plugins,
			"registry": registry
		}
		return ApiResponse(status=Status.SUCCESS, message='', data=data)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.get("/active")
async def get_active_plugins(request: Request):
	"""List active plugins"""
	try:
		bot = get_bot(request.app.state.bot)

		active_plugins = bot.mad_hatter.load_active_plugins_from_db()

		# plugins are managed by the MadHatter class
		plugins = []
		for p in bot.mad_hatter.plugins.values():
			manifest = deepcopy(p.manifest)  # we make a copy to avoid modifying the plugin obj
			manifest["active"] = p.id in active_plugins  # pass along if plugin is active or not
			if manifest["active"]:
				plugins.append(manifest)

		return ApiResponse(status=Status.SUCCESS, message='', data=plugins)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/upload")
async def install_plugin(
	request: Request,
	file: UploadFile,
	background_tasks: BackgroundTasks
):
	"""Install a new plugin from a zip file"""
	try:
		bot = get_bot(request.app.state.bot)

		admitted_mime_types = ["application/zip", 'application/x-tar']
		content_type = mimetypes.guess_type(file.filename)[0]
		if content_type not in admitted_mime_types:
			raise Exception(
				f'MIME type `{file.content_type}` not supported. Admitted types: {", ".join(admitted_mime_types)}')

		log(f"Uploading {content_type} plugin {file.filename}", "INFO")
		temp = NamedTemporaryFile(delete=False, suffix=file.filename)
		contents = file.file.read()
		with temp as f:
			f.write(contents)

		background_tasks.add_task(
			bot.mad_hatter.install_plugin, temp.name
		)

		data = {
			"filename": file.filename,
			"content_type": file.content_type,
			"info": "Plugin is being installed asynchronously"
		}
		return ApiResponse(status=Status.SUCCESS, message='', data=data)
	except Exception as e:
		return Response(status_code=400, content=e.__str__())


@router.post("/upload-registry")
async def install_plugin_from_registry(
	request: Request,
	background_tasks: BackgroundTasks,
	url_repo: Dict = Body(example={"url": "https://github.com/plugin-dev-account/plugin-repo"})
):
	"""Install a new plugin from external repository"""
	try:
		# search for a release on GitHub
		path_url = str(urlparse(url_repo["url"]).path)
		url = "https://api.github.com/repos" + path_url + "/releases"
		response = requests.get(url)
		if response.status_code != 200:
			raise Exception({"error": "Github API not available"})

		response = response.json()

		# Check if there are files for the latest release
		if len(response) != 0:
			url_zip = response[0]["assets"][0]["browser_download_url"]
		else:
			# if not, than download the zip repo
			# TODO: extracted folder still contains branch name
			url_zip = url_repo["url"] + "/archive/master.zip"

		# Get plugin name
		arr = path_url.split("/")
		arr.reverse()
		plugin_name = arr[0] + ".zip"

		with requests.get(url_zip, stream=True) as response:
			if response.status_code != 200:
				raise Exception({"error": "Download GitHub release failed"})

			with NamedTemporaryFile(delete=False, mode="w+b", suffix=plugin_name) as file:
				for chunk in response.iter_content(chunk_size=8192):
					file.write(chunk)
				log(f"Uploading plugin {plugin_name}", "INFO")

				# access bot instance
				bot = request.app.state.bot

				background_tasks.add_task(
					bot.mad_hatter.install_plugin, file.name
				)

				data = {
					"filename": file.name,
					"content_type": mimetypes.guess_type(plugin_name)[0],
					"info": "Plugin is being installed asynchronously"
				}

		return ApiResponse(status=Status.SUCCESS, message='', data=data)
	except Exception as e:
		return Response(status_code=400, content=e.__str__())


@router.put("/toggle/{plugin_id}", status_code=200)
async def toggle_plugin(plugin_id: str, request: Request):
	"""Enable or disable a single plugin"""

	try:
		bot = request.app.state.bot

		# check if plugin exists
		if not bot.mad_hatter.plugin_exists(plugin_id):
			raise HTTPException(
				status_code=404,
				detail={"error": "Plugin not found"}
			)

		# toggle plugin
		bot.mad_hatter.toggle_plugin(plugin_id)

		data = {
			"info": f"Plugin {plugin_id} toggled"
		}

		return ApiResponse(status=Status.SUCCESS, message='', data=data)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.get("/{plugin_id}")
async def get_plugin_details(plugin_id: str, request: Request):
	"""Returns information on a single plugin"""
	try:
		bot = request.app.state.bot

		if not bot.mad_hatter.plugin_exists(plugin_id):
			raise Exception({"error": "Plugin not found"})

		active_plugins = bot.mad_hatter.load_active_plugins_from_db()

		# get manifest and active True/False. We make a copy to avoid modifying the original obj
		plugin_info = deepcopy(bot.mad_hatter.plugins[plugin_id].manifest)
		plugin_info["active"] = plugin_id in active_plugins

		data = {
			"data": plugin_info
		}
		return ApiResponse(status=Status.SUCCESS, message='', data=data)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.delete("/{plugin_id}")
async def delete_plugin(plugin_id: str, request: Request):
	"""Physically remove plugin."""
	try:
		bot = request.app.state.bot

		if not bot.mad_hatter.plugin_exists(plugin_id):
			raise Exception({"error": "Item not found"})

		# remove folder, hooks and tools
		bot.mad_hatter.uninstall_plugin(plugin_id)

		data = {
			"deleted": plugin_id
		}

		return ApiResponse(status=Status.SUCCESS, message='', data=data)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
