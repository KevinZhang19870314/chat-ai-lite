"""Hooks to modify the BlackHole's documents ingestion.

Here is a collection of methods to hook into the BlackHole execution pipeline.

These hooks allow to intercept the uploaded documents at different places before they are saved into memory.

"""
import re
from typing import List

from log import log
from langchain.text_splitter import RecursiveCharacterTextSplitter
from mad_hatter.decorators import hook
from langchain.docstore.document import Document


# Hook called just before of inserting a document in vector memory
@hook(priority=0)
def before_blackhole_insert_memory(doc: Document, bot) -> Document:
	"""Hook the `Document` before is inserted in the vector memory.

	Allows to edit and enhance a single `Document` before the *BlackHole* add it to the declarative vector memory.

	The `Document` has two properties::

			`page_content`: the string with the text to save in memory;
			`metadata`: a dictionary with at least two keys:
					`source`: where the text comes from;
					`when`: timestamp to track when it's been uploaded.

	Args:
			doc: langchain `Document` to be inserted in memory.
			bot: Cheshire Bot instance.

	Returns:
			langchain `Document` that is added in the declarative vector memory.

	"""
	try:
		raw_filename = doc.metadata["source"]
		match = re.search(r'\((.*?)\)(.*)', raw_filename)
		if match:
			raw_filename = match.group(2)
			doc.metadata["source"] = raw_filename
	except Exception as e:
		pass
	return doc


# Hook called just before blackhole splits text. Input is whole Document
@hook(priority=0)
def before_blackhole_splits_text(doc: Document, bot) -> Document:
	"""Hook the `Document` before is split.

	Allows to edit the whole uploaded `Document` before the *BlackHole* recursively splits it in shorter ones.

	For instance, the hook allows to change the text or edit/add metadata.

	Args:
			doc: langchain `Document` uploaded in the *BlackHole* to be ingested.
			bot: Cheshire Bot instance.

	Returns:
			Edited langchain `Document`.

	"""
	return doc


# Hook called when blackhole splits text. Input is whole Document
@hook(priority=0)
def blackhole_splits_text(text, chunk_size: int, chunk_overlap: int, bot) -> List[Document]:
	"""Hook into the recursive split pipeline.

	Allows to edit the recursive split the *BlackHole* applies to chunk the ingested documents.

	This is applied when ingesting a documents and urls from a script, using an endpoint or from the GUI.

	Args:
			text: list of langchain `Document` to chunk.
			chunk_size: length of every chunk in characters.
			chunk_overlap: amount of overlap between consecutive chunks.
			bot: Cheshire Bot instance.

	Returns:
			list of chunked langchain `Document` to be optionally summarized and stored in episodic memory.

	"""

	# text splitter
	text_splitter = RecursiveCharacterTextSplitter(
		chunk_size=chunk_size,
		chunk_overlap=chunk_overlap,
		separators=["\\n\\n", "\n\n", ".\\n", ".\n", "\\n", "\n", " ", ""],
	)

	# split text
	docs = text_splitter.split_documents(text)

	# remove short texts (page numbers, isolated words, etc.)
	docs = list(filter(lambda d: len(d.page_content) > 10, docs))

	return docs


# Hook called after blackhole have splitted text into chunks.
#   Input is the chunks
@hook(priority=0)
def after_blackhole_splitted_text(chunks: List[Document], bot) -> List[Document]:
	"""Hook the `Document` after is split.

	Allows to edit the list of `Document` right after the *BlackHole* chunked them in smaller ones.

	Args:
			chunks: list of langchain `Document`.
			bot: Cheshire Bot instance.

	Returns:
			list of modified chunked langchain `Document` to be optionally summarized and stored in episodic memory.

	"""

	return chunks


# Hook called when a list of Document is going to be inserted in memory from the rabbit hole.
# Here you can edit/summarize the documents before inserting them in memory
# Should return a list of documents (each is a langchain Document)
@hook(priority=0)
def before_blackhole_stores_documents(docs: List[Document], bot) -> List[Document]:
	"""Hook into the memory insertion pipeline.

	Allows to modify how the list of `Document` is inserted in the vector memory.

	For example, this hook is a good point to summarize the incoming documents and save both original and
	summarized contents.
	An official plugin is available to test this procedure.

	Parameters
	----------
	docs : List[Document]
			List of Langchain `Document` to be edited.
	bot: DeepAI
			DeepAI Bot instance.

	Returns
	-------
	docs : List[Document]
			List of edited Langchain documents.

	"""

	return docs
