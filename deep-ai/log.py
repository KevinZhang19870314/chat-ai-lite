"""The log engine."""
import codecs
import json
import logging
import os
import sys

import colorlog as colorlog
from dotenv import load_dotenv

load_dotenv()


def get_log_level():
	"""Return the global LOG level."""
	return os.getenv("LOG_LEVEL", "ERROR")


class Log:
	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.LOG_LEVEL = get_log_level()
		self.logger.setLevel(self.LOG_LEVEL)

		formatter = colorlog.ColoredFormatter(
			"%(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
			datefmt="%Y-%m-%d %H:%M:%S",  # Custom date format
			reset=True,
			log_colors={
				'DEBUG': 'cyan',
				'INFO': 'green',
				'WARNING': 'yellow',
				'ERROR': 'red',
				'CRITICAL': 'red,bg_white',
			},
			secondary_log_colors={},
			style='%'
		)

		stream = codecs.getwriter('utf-8')(sys.stdout.buffer)
		console_handler = logging.StreamHandler(stream)
		console_handler.setFormatter(formatter)
		self.logger.addHandler(console_handler)

	def format_log_message(self, message):
		if isinstance(message, (list, dict)):
			try:
				return json.dumps(message, indent=4, ensure_ascii=False)
			except TypeError:
				return repr(message)
		elif hasattr(message, '__dict__'):
			try:
				return json.dumps(message.__dict__, indent=4, ensure_ascii=False)
			except TypeError:
				return repr(message)
		else:
			return str(message)

	def log(self, message, level="INFO"):
		try:
			formatted_message = self.format_log_message(message)
		except json.JSONDecodeError:
			formatted_message = message

		if level == "DEBUG":
			self.logger.debug(formatted_message)
		elif level == "INFO":
			self.logger.info(formatted_message)
		elif level == "WARNING":
			self.logger.warning(formatted_message)
		elif level == "ERROR":
			self.logger.error(formatted_message)
		elif level == "CRITICAL":
			self.logger.critical(formatted_message)
		else:
			raise ValueError("Invalid log level: {}".format(level))


logEngine = Log()


def log(msg, level="DEBUG"):
	"""Create function wrapper to class."""
	global logEngine
	return logEngine.log(msg, level)
