from abc import ABC

from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from langchain_community.document_loaders import UnstructuredWordDocumentLoader

from background.processor_strategy import ProcessorStrategy
from background.processor_utils import ProcessorUtils
from log import log


class WordProcessor(ProcessorStrategy, ABC):

	def __init__(self, bot, file_path: str):
		self.bot = bot
		self.file_path = file_path

	def execute(self) -> list[Document]:
		loader = UnstructuredWordDocumentLoader(self.file_path)
		raw_docs = loader.load()

		docs = ProcessorUtils.split_text(self.bot, raw_docs, 800, 10)

		tokens = ProcessorUtils.num_tokens_from_string(docs.__str__())
		log(f"Used tokens after embeddings: {tokens}", 'INFO')

		return docs

	def get_contents(self) -> str:
		loader = UnstructuredWordDocumentLoader(self.file_path)
		raw_docs = loader.load()

		# convert the raw docs to a string
		contents = ''.join([doc.page_content for doc in raw_docs])
		return contents
