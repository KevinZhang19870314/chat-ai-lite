import json
import time
from urllib.parse import urlencode

import requests
from fastapi import HTTPException
from langchain_core.documents import Document
from starlette import status

from db.crud_user import redis_client
from log import log
from typing import Any
from dataclasses import dataclass


@dataclass
class FeishuNode:
	creator: str
	has_child: bool
	node_create_time: str
	node_token: str
	node_type: str
	obj_create_time: str
	obj_edit_time: str
	obj_token: str
	obj_type: str
	origin_node_token: str
	origin_space_id: str
	owner: str
	parent_node_token: str
	space_id: str
	title: str

	@staticmethod
	def from_dict(obj: Any) -> 'FeishuNode':
		_creator = str(obj.get("creator"))
		_has_child = bool(obj.get("has_child"))
		_node_create_time = str(obj.get("node_create_time"))
		_node_token = str(obj.get("node_token"))
		_node_type = str(obj.get("node_type"))
		_obj_create_time = str(obj.get("obj_create_time"))
		_obj_edit_time = str(obj.get("obj_edit_time"))
		_obj_token = str(obj.get("obj_token"))
		_obj_type = str(obj.get("obj_type"))
		_origin_node_token = str(obj.get("origin_node_token"))
		_origin_space_id = str(obj.get("origin_space_id"))
		_owner = str(obj.get("owner"))
		_parent_node_token = str(obj.get("parent_node_token"))
		_space_id = str(obj.get("space_id"))
		_title = str(obj.get("title"))
		return FeishuNode(_creator, _has_child, _node_create_time, _node_token, _node_type, _obj_create_time,
											_obj_edit_time, _obj_token, _obj_type, _origin_node_token, _origin_space_id, _owner,
											_parent_node_token, _space_id, _title)


class Feishu:

	def __init__(self, app_id=None, app_secret=None):
		if not app_id:
			raise ValueError("user_access_token is required")
		if not app_secret:
			raise ValueError("app_secret is required")

		self.app_id = app_id
		self.app_secret = app_secret

	def bearer_user_access_token(self, user_access_token):
		if isinstance(user_access_token, bytes):
			user_access_token = user_access_token.decode('utf-8')
		return {
			'Authorization': f'Bearer {user_access_token}',
			'Content-Type': 'application/json'
		}

	def bearer_app_access_token(self, app_access_token):
		if isinstance(app_access_token, bytes):
			app_access_token = app_access_token.decode('utf-8')
		return {
			'Authorization': f'Bearer {app_access_token}',
			'Content-Type': 'application/json'
		}

	def get_authorize_url(self, redirect_uri):
		params = {
			'app_id': self.app_id,
			'redirect_uri': redirect_uri,
			'state': 'STATE',  # 自定义状态参数，用于防止CSRF攻击
			'scope': 'wiki:wiki:readonly docx:document:readonly docs:doc:readonly',
		}

		query_string = urlencode(params)
		authorize_url = f"https://open.feishu.cn/open-apis/authen/v1/authorize?{query_string}"
		return authorize_url

	def get_app_access_token(self):
		url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
		payload = json.dumps({
			"app_id": self.app_id,
			"app_secret": self.app_secret
		})

		headers = {
			'Content-Type': 'application/json'
		}

		response = requests.request("POST", url, headers=headers, data=payload)
		result = response.json()
		if response.status_code == 200 and result.get('code') == 0:
			data = result.get('app_access_token', None)
		else:
			log(f"Failed to get_app_access_token: {result.get('msg')}")
			raise Exception(f"Failed to get_app_access_token: {result.get('msg')}")

		return data

	def get_user_access_token(self, code: str, app_access_token: str):
		url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
		payload = json.dumps({
			"code": code,
			"grant_type": "authorization_code"
		})

		response = requests.request("POST", url, headers=self.bearer_app_access_token(app_access_token), data=payload)
		result = response.json()
		if response.status_code == 200 and result.get('code') == 0:
			data = result.get('data', None)
		else:
			log(f"Failed to get_user_access_token: {result.get('msg')}")
			raise Exception(f"Failed to get_user_access_token: {result.get('msg')}")

		return data

	def get_user_info(self, user_access_token: str):
		url = "https://open.feishu.cn/open-apis/authen/v1/user_info"
		payload = ''

		response = requests.request("GET", url, headers=self.bearer_user_access_token(user_access_token), data=payload)
		result = response.json()
		if response.status_code == 200 and result.get('code') == 0:
			data = result.get('data', None)
		else:
			log(f"Failed to get_user_info: {result.get('msg')}")
			raise Exception(f"Failed to get_user_info: {result.get('msg')}")

		return data

	def refresh_access_token(self, refresh_token: str, app_access_token: str):
		url = "https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token"
		payload = json.dumps({
			"grant_type": "refresh_token",
			"refresh_token": refresh_token
		})

		response = requests.request("POST", url, headers=self.bearer_app_access_token(app_access_token), data=payload)
		result = response.json()
		if response.status_code == 200 and result.get('code') == 0:
			data = result.get('data', None)
		else:
			log(f"Failed to refresh_access_token: {result.get('msg')}")
			# raise Exception(f"Failed to refresh_access_token: {result.get('msg')}")
			raise HTTPException(
				status_code=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED,
				detail=f"Failed to refresh_access_token: {result.get('msg')}",
				headers={"WWW-Authenticate": "Bearer"},
			)

		return data

	def get_all_nodes(self, user_access_token: str, space_id='6963978910325293060', parent_node_token=None):
		"""
		递归获取当前父节点下所有子节点信息

		默认获取G2 Space ID的某父节点下所有子节点： 6963978910325293060
		"""
		nodes_url = f"https://open.feishu.cn/open-apis/wiki/v2/spaces/{space_id}/nodes"
		nodes = []
		page_token = None

		while True:
			# Prepare parameters for the request
			params = {
				'page_size': 50  # Adjust the page_size as needed
			}
			if parent_node_token:
				params['parent_node_token'] = parent_node_token
			if page_token:
				params['page_token'] = page_token

			response = requests.get(nodes_url, headers=self.bearer_user_access_token(user_access_token), params=params)
			result = response.json()

			# Check for a successful response
			if response.status_code == 200 and result.get('code') == 0:
				data = result.get('data', {})
				nodes.extend(data.get('items', []))

				# Check if there are more items to fetch
				if not data.get('has_more'):
					break

				# Update page_token for the next loop iteration
				page_token = data.get('page_token')
			else:
				log(f"Failed to get_all_nodes: {result.get('msg')}")
				break

		# Create a separate list to store all child nodes
		all_child_nodes = []

		# Now go through all nodes and fetch children of nodes that have children
		for node in nodes:
			if node.get('has_child'):
				# Recursive call to get child nodes
				child_nodes = self.get_all_nodes(user_access_token, space_id, node.get('node_token'))
				all_child_nodes.extend(child_nodes)  # Add child nodes to the separate list

		# Combine parent nodes with their children to prevent duplicates
		nodes.extend(all_child_nodes)

		return nodes

	@staticmethod
	def to_feishu_node_list(nodes):
		return [FeishuNode.from_dict(node) for node in nodes]

	def get_raw_content(self, user_access_token: str, document_id):
		"""新版飞书获取文本内容: 文档类型：docx"""
		node_raw_content_url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/raw_content?lang=0"
		payload = ''
		response = requests.request("GET", node_raw_content_url, headers=self.bearer_user_access_token(user_access_token),
																data=payload)
		result = response.json()

		# Check for a successful response
		content = ''
		if response.status_code == 200 and result.get('code') == 0:
			data = result.get('data', {})
			content = data.get('content', '')
		else:
			log(f"Failed to get_raw_content: {result.get('msg')}")

		return content

	def get_old_raw_content(self, user_access_token: str, document_id):
		"""旧版飞书获取文本内容: 文档类型：doc"""
		node_raw_content_url = f"https://open.feishu.cn/open-apis/doc/v2/{document_id}/raw_content"
		payload = ''
		response = requests.request("GET", node_raw_content_url, headers=self.bearer_user_access_token(user_access_token),
																data=payload)
		result = response.json()

		# Check for a successful response
		content = ''
		if response.status_code == 200 and result.get('code') == 0:
			data = result.get('data', {})
			content = data.get('content', '')
		else:
			log(f"Failed to get_raw_content: {result.get('msg')}")

		return content

	@staticmethod
	def build_document(node: FeishuNode, content: str):
		document: Document = Document(page_content=content, metadata={})
		document.metadata['source'] = node.title
		document.metadata['when'] = time.time()
		document.metadata['node'] = node

		return document

	def ingest_documents(self, db, user_access_token: str, knowledge_base_id: str, space_id: str, parent_node_token: str, folder_path: str, bot):
		"""
		获取parent_node_token节点下所有飞书文档，并处理embeddings文档到向量知识库
		:param db: db session
		:param user_access_token: 飞书用户token
		:param knowledge_base_id: 向量知识库id
		:param space_id: 飞书知识库空间id
		:param parent_node_token: 飞书知识库父节点id
		:param folder_path: 向量知识库文件夹路径
		:param bot: bot实例
		:return:
		"""
		nodes = self.get_all_nodes(user_access_token, space_id, parent_node_token)
		node_list = self.to_feishu_node_list(nodes)
		docs: list[Document] = []
		for node in node_list:
			if node.obj_type.lower() == 'doc':
				raw_content = self.get_old_raw_content(user_access_token, node.obj_token)
				doc = Feishu.build_document(node, raw_content)
				docs.append(doc)
			elif node.obj_type.lower() == 'docx':
				raw_content = self.get_raw_content(user_access_token, node.obj_token)
				doc = Feishu.build_document(node, raw_content)
				docs.append(doc)

		# process docs
		log(f"Total {len(docs)} docs")
		for doc in docs:
			bot.black_hole.process_feishu_docs(db, knowledge_base_id, [doc], folder_path)
		return ''

	@staticmethod
	def cache_user_access_token(email, user_access_token):
		cache_key = f"feishu_user_access_token_{email}"
		# 设置过期时间为2小时，因为飞书用户token最长过期时间为2小时
		redis_client.set(cache_key, user_access_token, ex=7200)

	@staticmethod
	def get_cached_user_access_token(email):
		cache_key = f"feishu_user_access_token_{email}"
		return redis_client.get(cache_key)

