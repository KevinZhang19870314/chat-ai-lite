import tiktoken


class ProcessorUtils:
	@staticmethod
	def split_text(bot, text, chunk_size, chunk_overlap):
		# do something on the text before it is splitted
		text = bot.mad_hatter.execute_hook(
			"before_blackhole_splits_text", text
		)

		# split the documents using chunk_size and chunk_overlap
		docs = bot.mad_hatter.execute_hook(
			"blackhole_splits_text", text, chunk_size, chunk_overlap
		)

		# do something on the text after it is splitted
		docs = bot.mad_hatter.execute_hook(
			"after_blackhole_splitted_text", docs
		)

		return docs

	@staticmethod
	def num_tokens_from_string(string: str, encoding_name: str = 'cl100k_base') -> int:
		"""Returns the number of tokens in a text string."""
		encoding = tiktoken.get_encoding(encoding_name)
		num_tokens = len(encoding.encode(string))
		return num_tokens
