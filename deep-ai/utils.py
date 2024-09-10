"""Various utiles used from the projects."""
import random
import string
import time
from datetime import timedelta
from typing import Any

from langchain_core.runnables import RunnableSerializable, Runnable
from pydub import AudioSegment

from db import models


def to_camel_case(text):
	"""Take in a string of words separated by either hyphens or underscores and returns a string of words in camel case."""
	s = text.replace("-", " ").replace("_", " ").capitalize()
	s = s.split()
	if len(text) == 0:
		return text
	return s[0] + "".join(i.capitalize() for i in s[1:])


def verbal_timedelta(td):
	"""Convert a timedelta in human form."""
	if td.days != 0:
		abs_days = abs(td.days)
		if abs_days > 7:
			abs_delta = "{} weeks".format(td.days // 7)
		else:
			abs_delta = "{} days".format(td.days)
	else:
		abs_minutes = abs(td.seconds) // 60
		if abs_minutes > 60:
			abs_delta = "{} hours".format(abs_minutes // 60)
		else:
			abs_delta = "{} minutes".format(abs_minutes)
	if td < timedelta(0):
		return "{} ago".format(abs_delta)
	else:
		return "{} ago".format(abs_delta)


def calculate_audio_duration(file_object):
	audio = AudioSegment.from_file(file_object)
	duration_in_minutes = len(audio) / 1000 / 60  # Convert milliseconds to seconds
	print(f"Duration in minutes: {duration_in_minutes}")
	return duration_in_minutes


def whisper_costs(file_object):
	# Whisper	$0.006 / minute (rounded to the nearest second)
	rate_per_minute = 0.006
	duration_in_minutes = calculate_audio_duration(file_object)
	cost = rate_per_minute * round(duration_in_minutes, 2)

	return cost


def generate_session_id():
	timestamp = str(int(time.time() * 1000))  # Get current timestamp in milliseconds
	random_num = str(random.randint(0, 9999)).zfill(4)  # Generate a random number with padding

	session_id = timestamp + random_num  # Concatenate timestamp and random number
	return int(session_id)


def generate_random_string(length=6):
	# Define the characters and numbers to use
	characters = string.ascii_letters + string.digits
	# Generate a random string of specified length
	random_string = ''.join(random.choice(characters) for i in range(length))
	return random_string


def config_metadata_chain(chain: RunnableSerializable[dict, str] | RunnableSerializable[Any, str], metadata: dict):
	chain = chain.with_config({"metadata": metadata})
	return chain


def config_user_metadata_chain(
	chain: RunnableSerializable[dict, str] | RunnableSerializable[Any, str],
	user: models.User
) -> Runnable:
	chain = chain.with_config({"metadata": models.UserPayload(**user.dict()).dict()})
	return chain
