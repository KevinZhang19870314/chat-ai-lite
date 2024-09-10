FROM python:3.10.1-slim-buster

WORKDIR /app

COPY requirements.txt .

# for ffmpeg, calculate_audio_duration
RUN apt-get update && \
	apt-get install -y ffmpeg libavcodec-extra

RUN --mount=type=cache,target=/root/.cache/pip \
	pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "home"]
