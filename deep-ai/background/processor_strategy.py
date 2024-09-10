from abc import ABC, abstractmethod

from langchain.schema import Document


# Strategy interface
class ProcessorStrategy(ABC):
	@abstractmethod
	def execute(self) -> list[Document]:
		pass

	@abstractmethod
	def get_contents(self) -> str:
		pass
