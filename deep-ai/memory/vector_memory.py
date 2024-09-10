import os
from typing import Optional, List

import numpy as np
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores.faiss import FAISS

from log import log


class VectorMemory:
	def __init__(self, bot, verbose=False) -> None:
		self.bot = bot
		self.verbose = verbose

		# Get embedder from bot instance
		self.embedder = bot.embedder

		if self.embedder is None:
			raise Exception("No embedder passed to VectorMemory")

		self.common_storage = os.getenv('COMMON_STORAGE')

	def refresh_embedder(self, embedder):
		self.embedder = embedder

	def faiss_db(self, index_name: str = 'index', folder_path=None) -> FAISS:
		user_db = VectorMemoryCollection.build(
			bot=self.bot,
			folder_path=self.common_storage if folder_path is None else folder_path,
			embeddings=self.embedder,
			index_name=str(index_name)
		)

		return user_db

	def remove(self, index_name: str, ids: Optional[List[str]], folder_path=None):
		"""
		Function to remove documents from the vectorstore.
		"""
		vectorstore = self.faiss_db(index_name, folder_path)
		faiss_db, removed, total = VectorMemoryCollection.remove(vectorstore, ids)
		log(f"Total documents before removal: {total}", 'INFO')
		log(f"Removed {removed} documents from index name: {index_name}", 'INFO')
		faiss_db.save_local(self.common_storage if folder_path is None else folder_path, index_name)
		return faiss_db


class VectorMemoryCollection:
	@staticmethod
	def build(
		bot,
		folder_path: str,
		embeddings: Embeddings | None = None,
		index_name: str = "index"
	) -> FAISS:
		try:
			log(f"Load existing FAISS db {folder_path}, index name is {index_name}", 'INFO')
			faiss_db = FAISS.load_local(folder_path, embeddings, index_name, allow_dangerous_deserialization=True)
			log(f"{index_name} Loaded", 'INFO')
			return faiss_db
		except RuntimeError as re:
			log(re.__str__(), 'DEBUG')
			log(f"New FAISS db {folder_path}, index name is {index_name}", 'INFO')
			os.makedirs(folder_path, exist_ok=True)
			db = FAISS.from_texts(texts=["Hello, Deep AI!"], embedding=embeddings, metadatas=[{"name": "Hello"}])
			db.save_local(folder_path, index_name)
			faiss_db = FAISS.load_local(folder_path, embeddings, index_name, allow_dangerous_deserialization=True)
			log(f"{index_name} Loaded", 'INFO')
			return faiss_db

	@staticmethod
	def remove(vectorstore: FAISS, docstore_ids: Optional[List[str]]):
		"""
		Function to remove documents from the vectorstore.

		Parameters
		----------
		vectorstore : FAISS
				The vectorstore to remove documents from.
		docstore_ids : Optional[List[str]]
				The list of docstore ids to remove. If None, all documents are removed.

		Returns
		-------
		vectorstore: FAISS
				The vectorstore after removing the documents.
		n_removed : int
				The number of documents removed.
		n_total : int
				The total number of documents in the vectorstore.

		Raises
		------
		ValueError
				If there are duplicate ids in the list of ids to remove.
		"""
		if docstore_ids is None:
			vectorstore.docstore = {}
			vectorstore.index_to_docstore_id = {}
			n_removed = vectorstore.index.ntotal
			n_total = vectorstore.index.ntotal
			vectorstore.index.reset()
			return vectorstore, n_removed, n_total
		set_ids = set(docstore_ids)
		if len(set_ids) != len(docstore_ids):
			raise ValueError("Duplicate ids in list of ids to remove.")
		index_ids = [
			i_id
			for i_id, d_id in vectorstore.index_to_docstore_id.items()
			if d_id in docstore_ids
		]
		n_removed = len(index_ids)
		n_total = vectorstore.index.ntotal
		vectorstore.index.remove_ids(np.array(index_ids, dtype=np.int64))
		for i_id, d_id in zip(index_ids, docstore_ids):
			del vectorstore.docstore._dict[
				d_id
			]  # remove the document from the docstore

			del vectorstore.index_to_docstore_id[
				i_id
			]  # remove the index to docstore id mapping
		vectorstore.index_to_docstore_id = {
			i: d_id
			for i, d_id in enumerate(vectorstore.index_to_docstore_id.values())
		}
		return vectorstore, n_removed, n_total

	@staticmethod
	def is_folder_empty(folder_path):
		# Check if the folder exists
		if not os.path.exists(folder_path):
			return True

		# Get the list of files and folders in the given folder
		contents = os.listdir(folder_path)

		# Return True if the folder is empty, False otherwise
		return len(contents) == 0
