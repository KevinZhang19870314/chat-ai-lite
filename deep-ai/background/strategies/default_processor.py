from abc import ABC

from langchain.schema import Document

from background.processor_strategy import ProcessorStrategy


class DefaultProcessor(ProcessorStrategy, ABC):
	def execute(self) -> list[Document]:
		return []
