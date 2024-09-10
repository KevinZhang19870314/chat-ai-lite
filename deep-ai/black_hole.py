import json
import os
import re
import time
import traceback
import uuid
from typing import List

from fastapi import UploadFile
from langchain.docstore.document import Document
from langchain_community.vectorstores.faiss import FAISS

from background.processor_context import ProcessorContext, DOCS_TYPE
from db import models, crud_vectordocrecord
from log import log


class BlackHole:
	def __init__(self, bot, storage_path: str = None):
		self.bot = bot
		self.upload_path = bot.upload_path
		self.common_storage = storage_path if storage_path else bot.common_storage
		self.knowledge_base_id = None
		self.raw_filename = None
		self.processor_context = ProcessorContext(bot)

	def save_uploaded_file_to_path(self, file: UploadFile, filename: str = None):
		if filename is None:
			filename = file.filename
		response = BlackHole.save_file_to_path(file, self.upload_path, filename)
		return response

	def process_file(self, file_name: str):
		file_path = os.path.join(self.upload_path, file_name)
		log(f"Processing file {file_path}", 'INFO')

		match = re.search(r'\((.*?)\)(.*)', file_name)
		if match:
			self.knowledge_base_id = match.group(1)
			self.raw_filename = match.group(2)
		else:
			self.knowledge_base_id = None
			self.raw_filename = None
			log(f"No knowledge_base_id in file {file_name}, please check upload_file endpoint for issues")
			log(f"delete file due to no knowledge_base_id in file, please try again later", 'INFO')
			BlackHole.delete_file(file_path)
			return

		if os.path.isfile(file_path):
			try:
				self.processor_context.build_strategy(file_path)
				docs = self.processor_context.execute_strategy()

				doc_ids = self.store_documents(docs, file_name, self.common_storage)

				self.bulk_insert_records_to_db(self.knowledge_base_id, self.raw_filename, doc_ids)
				BlackHole.delete_file(file_path)
			except Exception as e:
				traceback.print_exc()
				log(f"Error when processing file {file_path}: {e}", 'INFO')
				log(f"delete file after error processing {file_path}, please try again later", 'INFO')
				BlackHole.delete_file(file_path)

	def process_feishu_docs(self, db, knowledge_base_id: str, docs: list[Document], folder_path: str):
		log(f"======Processing docs======", 'INFO')

		try:
			self.knowledge_base_id = knowledge_base_id
			self.raw_filename = docs[0].metadata["source"]
			self.processor_context.build_strategy(DOCS_TYPE, docs)
			docs = self.processor_context.execute_strategy()
			node = docs[0].metadata["node"]
			feishu_title = node.title
			feishu_obj_edit_time = node.obj_edit_time
			feishu_node = node

			# check if file is updated, if it is, then do embeddings; otherwise, do nothing
			records = crud_vectordocrecord.get_vector_doc_record_by_filename(db, self.knowledge_base_id, self.raw_filename)
			if len(records) > 0 and records[0].feishu_obj_edit_time >= feishu_obj_edit_time:
				log(f"file {self.raw_filename} is NOT updated, do nothing", 'INFO')
				return

			doc_ids = self.store_documents(docs, self.raw_filename, folder_path)

			# check records if exists for the same doc, if yes, delete.
			# (where filename = self.raw_filename and knowledge_base_id = self.knowledge_base_id)
			log(f"remove the vector doc records by filename {self.raw_filename} and knowledge_base_id {self.knowledge_base_id} in mysql", 'DEBUG')
			crud_vectordocrecord.delete_vector_doc_record_by_filename(db, knowledge_base_id, self.raw_filename)

			log(f"Bulk insert records to db, {doc_ids}", 'DEBUG')
			self.bulk_insert_records_to_db(
				self.knowledge_base_id,
				self.raw_filename,
				doc_ids,
				feishu_title=feishu_title,
				feishu_obj_edit_time=feishu_obj_edit_time,
				feishu_node=json.dumps(feishu_node.__dict__)
			)
		except Exception as e:
			traceback.print_exc()
			log(f"Error when processing docs: {e}", 'INFO')

	def store_documents(self, docs: List[Document], source: str, folder_path=None) -> list[str]:
		"""
		Load a list of Documents in the bot declarative memory.
		:param docs: a list of documents to store in memory
		:param source: a string representing the source,
				either the file name or the website URL
		:param folder_path: a string representing the folder path for vector store path
		:return: a list of document ids
		"""
		log(f"Preparing to memorize {len(docs)} vectors")
		faiss_db: FAISS = self.bot.memory.vectors.faiss_db(self.knowledge_base_id, folder_path)
		doc_ids = []

		# classic embed
		for d, doc in enumerate(docs):
			doc.metadata["source"] = source
			doc.metadata["when"] = time.time()
			doc = self.bot.mad_hatter.execute_hook(
				"before_blackhole_insert_memory", doc
			)
			inserting_info = f"{d + 1}/{len(docs)}):\nPage content: {doc.page_content}\nMetadata: {doc.metadata}"
			if doc.page_content != "":
				ids = faiss_db.add_texts(
					[doc.page_content],
					[doc.metadata],
				)

				log(f"doc id: {ids[0]}")
				doc_ids.append(ids[0])
				log(f"Inserted into memory({inserting_info})\n")
			else:
				log(f"Skipped memory insertion of empty doc ({inserting_info})")

			# wait a little to avoid APIs rate limit errors
			time.sleep(0.1)

		# save to disk
		log("Save the vector store embeddings to disk")
		faiss_db.save_local(folder_path, self.knowledge_base_id)
		log("Done uploading")
		return doc_ids

	def bulk_insert_records_to_db(self, knowledge_base_id: str, filename: str, doc_ids: list[str], **kwargs):
		records_to_db = []
		feishu_title = kwargs.get('feishu_title')
		feishu_obj_edit_time = kwargs.get('feishu_obj_edit_time')
		feishu_node = kwargs.get('feishu_node')
		for doc_id in doc_ids:
			records_to_db.append(models.VectorDocRecord(
				doc_id=doc_id,
				filename=filename,
				knowledge_base_id=knowledge_base_id,
				feishu_title=feishu_title,
				feishu_obj_edit_time=feishu_obj_edit_time,
				feishu_node=feishu_node
			))

		crud_vectordocrecord.bulk_insert_vector_doc_records(next(self.bot.db()), records_to_db)

	@staticmethod
	def delete_file(file_path: str):
		"""Delete file after processing"""
		try:
			os.remove(file_path)
		except Exception as e:
			log(f"Error when delete file {file_path}: {e.__str__()}", 'INFO')

	@staticmethod
	def save_file_to_path(file: UploadFile, path: str, filename: str, max_files: int = 10):
		# check path exists, if not, create
		if not os.path.exists(path):
			os.makedirs(path)

		count = BlackHole.count_files(path)
		if count >= max_files:
			raise Exception("Exceeded files limit, server only can processing 10 files per time")

		file_bytes = file.file.read()
		full_path = os.path.join(path, filename)

		with open(full_path, "wb") as f:
			f.write(file_bytes)

		return {"filename": filename, "full_path": full_path}

	@staticmethod
	def count_files(path):
		count = 0
		for root, dirs, files in os.walk(path):
			count += len(files)
		return count
