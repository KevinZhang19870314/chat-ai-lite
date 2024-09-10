from langchain.schema import Document

from background.processor_strategy import ProcessorStrategy
from background.processor_utils import ProcessorUtils
from log import log


class DocsProcessor(ProcessorStrategy):

	def __init__(self, bot, docs: list[Document]):
		self.bot = bot
		self.docs = docs

	def execute(self) -> list[Document]:
		raw_docs = self.docs

		docs = ProcessorUtils.split_text(self.bot, raw_docs, 4000, 200)

		tokens = ProcessorUtils.num_tokens_from_string(docs.__str__())
		log(f"Used tokens if do embeddings: {tokens}", 'INFO')

		return docs

	def get_contents(self) -> str:
		raw_docs = self.docs

		# convert the raw docs to a string
		contents = '\n'.join([doc.page_content for doc in raw_docs])
		return contents
