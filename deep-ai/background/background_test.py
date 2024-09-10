import mimetypes

from background.processor_context import ProcessorContext
from deep_ai import DeepAI

mimetypes.add_type("text/markdown", ".md")
mimetypes.add_type("text/markdown", ".markdown")
mimetypes.add_type("text/csv", ".csv")
mimetypes.add_type("application/msword", ".docx")

bot = DeepAI()
file_path = "C:\\Users\\kevin.zhang\\Downloads\\UCP - Admin Integration - GPAPI - Questions - 2023-06-30.csv"

context = ProcessorContext(bot)
context.build_strategy(file_path)
result = context.execute_strategy()

for d in result:
	print(d.page_content)
