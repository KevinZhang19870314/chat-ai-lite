import mimetypes

from langchain.schema import Document

from background.processor_strategy import ProcessorStrategy
from background.strategies.csv_processor import CsvProcessor
from background.strategies.docs_processor import DocsProcessor
from background.strategies.excel_processor import ExcelProcessor
from background.strategies.markdown_processor import MarkdownProcessor
from background.strategies.pdf_processor import PdfProcessor
from background.strategies.text_processor import TextProcessor
from background.strategies.word_processor import WordProcessor

DOCS_TYPE = "DOCS"


class ProcessorContext:
	strategy: ProcessorStrategy  # the strategy interface

	def __init__(self, bot):
		self.bot = bot

	def _get_strategy(self, file_path: str, docs: list[Document]) -> ProcessorStrategy:
		if file_path == DOCS_TYPE:
			return DocsProcessor(self.bot, docs)

		content_type, _ = mimetypes.guess_type(file_path)
		if content_type == "text/plain":
			processor = TextProcessor(self.bot, file_path)
		elif content_type == "text/markdown":
			processor = MarkdownProcessor(self.bot, file_path)
		elif content_type == "application/pdf":
			processor = PdfProcessor(self.bot, file_path)
		elif content_type == "text/csv":
			processor = CsvProcessor(self.bot, file_path)
		elif content_type == "application/msword":
			processor = WordProcessor(self.bot, file_path)
		elif content_type == "application/msexcel":
			processor = ExcelProcessor(self.bot, file_path)
		else:
			raise Exception("MIME type not supported for upload")

		return processor

	def build_strategy(self, file_path: str, docs: list[Document] = None) -> None:
		if docs is None:
			docs = []
		self.strategy = self._get_strategy(file_path, docs)

	def execute_strategy(self) -> list[Document]:
		return self.strategy.execute()

	def execute_get_contents(self) -> str:
		return self.strategy.get_contents()
