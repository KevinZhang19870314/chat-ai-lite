from abc import ABC

from langchain_community.document_loaders import CSVLoader
from langchain.schema import Document

from background.processor_strategy import ProcessorStrategy
from background.processor_utils import ProcessorUtils
from log import log


class CsvProcessor(ProcessorStrategy, ABC):

	def __init__(self, bot, file_path: str):
		self.bot = bot
		self.file_path = file_path

	def check_row_is_empty(self, row: list[str]) -> bool:
		try:
			for column in row:
				column_value = column.split(":")[1]
				if column_value.strip() != "":
					return False
			return True
		except:
			return False

	def execute(self) -> list[Document]:
		loader = CSVLoader(self.file_path)
		raw_docs = loader.load()
		filtered_docs = []
		for d in raw_docs:
			row = d.page_content.split("\n")
			if self.check_row_is_empty(row) is False:
				filtered_docs.append(d)

		docs = ProcessorUtils.split_text(self.bot, filtered_docs, 400, 0)

		tokens = ProcessorUtils.num_tokens_from_string(docs.__str__())
		log(f"Used tokens after embeddings: {tokens}", 'INFO')

		return docs
