from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document

from background.processor_strategy import ProcessorStrategy
from background.processor_utils import ProcessorUtils
from log import log


class PdfProcessor(ProcessorStrategy):

	def __init__(self, bot, file_path: str):
		self.bot = bot
		self.file_path = file_path

	def execute(self) -> list[Document]:
		loader = PyPDFLoader(self.file_path)
		docs = loader.load_and_split()
		# raw_docs = loader.load()
		#
		# docs = ProcessorUtils.split_text(self.bot, raw_docs, 4000, 400)
		#
		# tokens = ProcessorUtils.num_tokens_from_string(docs.__str__())
		# log(f"Used tokens after embeddings: {tokens}", 'INFO')

		return docs

	def get_contents(self) -> str:
		loader = PyPDFLoader(self.file_path)
		raw_docs = loader.load()

		# convert the raw docs to a string
		contents = '\n'.join([doc.page_content for doc in raw_docs])
		return contents
