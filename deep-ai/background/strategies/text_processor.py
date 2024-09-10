from langchain_community.document_loaders import TextLoader
from langchain.schema import Document

from background.processor_strategy import ProcessorStrategy
from background.processor_utils import ProcessorUtils
from log import log


class TextProcessor(ProcessorStrategy):

	def __init__(self, bot, file_path: str):
		self.bot = bot
		self.file_path = file_path

	def execute(self) -> list[Document]:
		loader = TextLoader(self.file_path, encoding="utf8")
		raw_docs = loader.load()

		docs = ProcessorUtils.split_text(self.bot, raw_docs, 4000, 200)

		summaries = self.bot.mad_hatter.execute_hook("before_blackhole_stores_documents", docs)

		docs = docs + summaries

		tokens = ProcessorUtils.num_tokens_from_string(docs.__str__())
		log(f"Used tokens after embeddings: {tokens}", 'INFO')

		return docs

	def get_contents(self) -> str:
		loader = TextLoader(self.file_path, encoding="utf8")
		raw_docs = loader.load()

		# convert the raw docs to a string
		contents = '\n'.join([doc.page_content for doc in raw_docs])
		return contents
